from datetime import datetime
import json
import logging
import threading
import time

import celery.result
import celery.states
import pytz
import z3c.celery.celery
import zope.app.appsetup.product
import zope.component
import zope.event
import zope.i18n
import zope.interface

from zeit.cms.content.interfaces import IUUID
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR, CAN_RETRACT_ERROR, PRIORITY_LOW
import zeit.cms.celery
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.publisher


logger = logging.getLogger(__name__)
timer_logger = logging.getLogger('zeit.workflow.timer')


@zope.component.adapter(zeit.cms.repository.interfaces.IRepositoryContent)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublish)
class Publish:
    def __init__(self, context):
        self.context = context

    def publish(self, priority=None, background=True, **kw):
        """Publish object."""
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        if info.can_publish() == CAN_PUBLISH_ERROR:
            raise zeit.cms.workflow.interfaces.PublishingError(
                'Publish pre-conditions not satisfied.'
            )

        return self._execute_task(
            PUBLISH_TASK,
            [self.context.uniqueId],
            priority,
            background,
            _('Publication scheduled'),
            **kw,
        )

    def retract(self, priority=None, background=True, **kw):
        """Retract object."""
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        try:
            if info.can_retract() == CAN_RETRACT_ERROR:
                raise zeit.cms.workflow.interfaces.RetractingError(
                    'Retracting pre-conditions not satisfied.'
                )
        except AttributeError:
            pass

        return self._execute_task(
            RETRACT_TASK,
            [self.context.uniqueId],
            priority,
            background,
            _('Retracting scheduled'),
            **kw,
        )

    def publish_multiple(self, objects, priority=PRIORITY_LOW, background=True, **kw):
        """Publish multiple objects."""
        if not objects:
            logger.warning(
                'Not starting a publishing task, because no objects' ' to publish were given'
            )
            return None
        ids = [self.context.uniqueId]
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.log(
                obj,
                _('Collective Publication of ${count} objects', mapping={'count': len(objects)}),
            )
            ids.append(obj.uniqueId)
        return self._execute_task(MULTI_PUBLISH_TASK, ids, priority, background, **kw)

    def retract_multiple(self, objects, priority=PRIORITY_LOW, background=True, **kw):
        """Retract multiple objects."""
        if not objects:
            logger.warning(
                'Not starting a retract task, because no objects' ' to retract were given'
            )
            return None
        ids = [self.context.uniqueId]
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.log(
                obj, _('Collective Retraction of ${count} objects', mapping={'count': len(objects)})
            )
            ids.append(obj.uniqueId)
        return self._execute_task(MULTI_RETRACT_TASK, ids, priority, background, **kw)

    def _execute_task(self, task, ids, priority, background, message=None, **kw):
        if background:
            if message:
                self.log(self.context, message)
            return task.apply_async((ids,), queue=self.get_priority(priority), **kw)
        else:
            result = task(ids)
            return celery.result.EagerResult('eager', result, celery.states.SUCCESS)

    def log(self, obj, msg):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, msg)

    def get_priority(self, priority):
        if priority is None:
            priority = zeit.cms.workflow.interfaces.IPublishPriority(self.context)
        return priority


class MultiPublishError(Exception):
    pass


MODE_PUBLISH = 'publish'
MODE_RETRACT = 'retract'


class PublishRetractTask:
    mode = NotImplemented  # MODE_PUBLISH or MODE_RETRACT

    def __init__(self, jobid):
        self.jobid = jobid
        self.context = None  # extension point for MultiTask

    def run(self, ids):
        """Run task in worker."""
        ids_str = ', '.join(ids)
        info = (type(self).__name__, ids_str, self.jobid)
        __traceback_info__ = info
        timer.start('Job %s started: %s (%s)' % info)
        logger.info('Running job %s for %s', self.jobid, ids_str)

        objs = []
        for uniqueId in ids:
            try:
                objs.append(self.repository.getContent(uniqueId))
            except KeyError:
                logger.warning('Not found %s, ignoring', uniqueId)
        timer.mark('Looked up object')

        try:
            result = self._run(objs)
        except z3c.celery.celery.Abort:
            raise
        except Exception as e:
            logger.error('Error during publish/retract', exc_info=True)
            messageid = 'Error during publish/retract: ${exc}: ${message}'
            if isinstance(e, MultiPublishError):
                to_log = []
                all_errors = []
                with_error = []
                for obj, error in e.args[0]:
                    logger.error('Nested error', exc_info=error)
                    # Like zeit.cms.browser.error.ErrorView.message
                    args = getattr(error, 'args', None)
                    if args:
                        errormessage = zope.i18n.translate(args[0], target_language='de')
                    else:
                        errormessage = str(error)

                    submessage = _(
                        messageid,
                        mapping={'exc': error.__class__.__name__, 'message': errormessage},
                    )
                    to_log.append((obj, submessage))
                    with_error.append(obj.uniqueId)
                    all_errors.append((obj, '%s: %s' % (error.__class__.__name__, errormessage)))
                if len(all_errors) == 1:
                    all_errors = all_errors[0][1]
                message = _(messageid, mapping={'exc': '', 'message': str(all_errors)})
            else:
                message = _(messageid, mapping={'exc': e.__class__.__name__, 'message': str(e)})
                to_log = [(obj, message) for obj in objs]
                with_error = [obj.uniqueId for obj in objs]

            if self.context is not None:
                to_log.append(
                    (
                        self.context,
                        _(
                            'Objects with errors: ${objects}',
                            mapping={'objects': ', '.join(sorted(with_error))},
                        ),
                    )
                )

            raise z3c.celery.celery.HandleAfterAbort(
                self._log_messages,
                to_log,
                message=zope.i18n.translate(message, target_language='de'),
            )
        else:
            return result
        finally:
            timer.mark('Done %s' % ids_str)
            timer_logger.debug('Timings:\n%s', timer)
            dummy, total, timer_message = timer.get_timings()[-1]
            logger.info('%s (%2.4fs)' % (timer_message, total))

    def _assign_publisher_errors_to_objects(self, exc, objects):
        errors = []
        msg = f'{exc.url} returned {exc.status}'
        if not exc.errors:
            e = PublishError(msg)
            for obj in objects:
                errors.append((obj, e))
        elif len(exc.errors) == 1 and not exc.errors[0].get('source'):
            e = PublishError.from_detail(msg, exc.errors[0])
            for obj in objects:
                errors.append((obj, e))
        else:
            errors.extend(self._assign_publisher_error_details(exc, objects))
        return errors

    def _assign_publisher_error_details(self, exc, objects):
        details = json.dumps(exc.errors)
        e = PublishError(f'{exc.url} returned {exc.status}, Details: {details}')
        errors = []
        for obj in objects:
            errors.append((obj, e))
        return errors

    def _log_messages(self, objs_and_messages):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        for obj, message in objs_and_messages:
            log.log(obj, message)

    def cycle(self, obj):
        """checkout/checkin obj to sync data as necessary.

        The basic idea is that there are some event handlers which sync
        properties to xml on checkout/checkin.

        """
        if not zeit.cms.content.interfaces.IXMLContent.providedBy(obj):
            return obj
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(obj)
        try:
            # We do not use the user's workingcopy but a "fresh" one which we
            # just throw away afterwards. This has two effects: 1. The users'
            # workingcopy istn't cluttered with ghosts and 2. we can publish in
            # parallel.
            checked_out = manager.checkout(temporary=True, publishing=True)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            logger.warning('Could not checkout %s' % obj.uniqueId)
            return obj
        manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
        try:
            obj = manager.checkin(publishing=True)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # XXX this codepath is not tested!
            logger.warning('Could not checkin %s' % obj.uniqueId)
            del checked_out.__parent__[checked_out.__name__]
            return obj
        timer.mark('Cycled %s' % obj.uniqueId)
        return obj

    def recurse(self, method, obj, *args):
        """Apply method recursively on obj."""
        config = zope.app.appsetup.product.getProductConfiguration('zeit.workflow') or {}
        DEPENDENCY_PUBLISH_LIMIT = int(config.get('dependency-publish-limit', 1))
        stack = [obj]
        seen = set()
        result_obj = None
        while stack:
            current_obj = stack.pop(0)
            if current_obj.uniqueId in seen:
                continue
            seen.add(current_obj.uniqueId)
            logger.debug('%s %s' % (method, current_obj.uniqueId))
            new_obj = method(current_obj, *args)
            timer.mark('Called %s on %s' % (method.__name__, current_obj.uniqueId))
            if len(seen) > DEPENDENCY_PUBLISH_LIMIT:
                # "strictly greater" comparison since the starting object
                # should not count towards the limit
                break

            # Dive into dependent objects
            deps = zeit.cms.workflow.interfaces.IPublicationDependencies(new_obj)
            if self.mode == MODE_PUBLISH:
                stack.extend(deps.get_dependencies())
            elif self.mode == MODE_RETRACT:
                stack.extend(deps.get_retract_dependencies())
            else:
                raise ValueError(
                    'Task mode must be %r or %r, not %r' % (MODE_PUBLISH, MODE_RETRACT, self.mode)
                )
            timer.mark('Got dependencies for %s' % (new_obj.uniqueId,))

            if result_obj is None:
                result_obj = new_obj

        return result_obj

    def serialize(self, obj, result):
        result.append(zeit.workflow.interfaces.IPublisherData(obj)(self.mode))
        return obj

    def log(self, obj, message):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, message)

    @property
    def repository(self):
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    @staticmethod
    def lock(obj, master=None):
        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(obj.uniqueId))
        lockable = zope.app.locking.interfaces.ILockable(obj, None)
        if lockable is not None and not lockable.ownLock():
            if lockable.locked():
                raise zope.app.locking.interfaces.LockingError(
                    _(
                        'The object ${name} is locked by ${user}.',
                        mapping={'name': obj.uniqueId, 'user': lockable.locker()},
                    )
                )
            lockable.lock(timeout=240)
        timer.mark('Locked %s' % obj.uniqueId)
        return obj

    @staticmethod
    def unlock(obj, master=None):
        lockable = zope.app.locking.interfaces.ILockable(obj, None)
        if lockable is not None and lockable.locked() and lockable.ownLock():
            lockable.unlock()
        timer.mark('Unlocked %s' % obj.uniqueId)
        return obj


class PublishError(Exception):
    @classmethod
    def from_detail(cls, message, error):
        msg = f'{message}: {error.get("title", "Unknown Error")}'
        if error.get('status'):
            msg += f' ({error["status"]})'
        if error.get('detail'):
            msg += f', Details: {error["detail"]}'
        return cls(msg)


class PublishTask(PublishRetractTask):
    """Publish object."""

    mode = MODE_PUBLISH

    def _run(self, objs):
        logger.info('Publishing %s' % ', '.join(obj.uniqueId for obj in objs))
        errors = []
        published = []
        for obj in objs:
            try:
                obj = self.recurse(self.can_publish, obj)
                obj = self.recurse(self.lock, obj, obj)
                obj = self.recurse(self.before_publish, obj, obj)
            except Exception as e:
                errors.append((obj, e))
            else:
                published.append(obj)

        to_publish = []
        for obj in published:
            try:
                deps = []
                self.recurse(self.serialize, obj, deps)
                to_publish.extend(deps)
            except Exception as e:
                errors.append((obj, e))

        try:
            if to_publish:
                publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
                publisher.request(to_publish, self.mode)
                timer.mark('Called publisher')
        except zeit.workflow.publisher.PublisherError as e:
            errors.extend(self._assign_publisher_errors_to_objects(e, published))
        except Exception as e:
            for obj in published:
                errors.append((obj, e))

        for obj in published:
            try:
                self.recurse(self.after_publish, obj, obj)
                obj = self.recurse(self.unlock, obj, obj)
            except Exception as e:
                errors.append((obj, e))

        if errors:
            raise MultiPublishError(errors)

        return 'Published.'

    def can_publish(self, obj):
        """at least check if the object can be published before
        setting published to True"""
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        if info.can_publish() == CAN_PUBLISH_ERROR:
            errors = []
            for error_message in info.error_messages:
                errors.append(zope.i18n.translate(error_message, target_language='de'))
            raise zeit.cms.workflow.interfaces.PublishingError(', '.join(errors))
        return obj

    def can_retract(self, obj):
        """at least check if the object can be retracted before
        setting published to True"""
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        if info.can_retract() == CAN_RETRACT_ERROR:
            errors = []
            for error_message in info.error_messages:
                errors.append(zope.i18n.translate(error_message, target_language='de'))
            raise zeit.cms.workflow.interfaces.RetractingError(', '.join(errors))
        return obj

    def before_publish(self, obj, master):
        """Do everything necessary before the actual publish."""
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = True
        info.date_last_published = datetime.now(pytz.UTC)
        timer.mark('Set date_last_published')
        if not info.date_first_released:
            info.date_first_released = info.date_last_published
            timer.mark('Set date_first_released')

        # XXX Yes this is not strictly _before_ publish. However, zeit.retresco
        # needs this point in time to perform its indexing, and the other
        # subscribers don't care either way, so it's probably not worth
        # introducing two separate events.
        zope.event.notify(zeit.cms.workflow.interfaces.BeforePublishEvent(obj, master))
        timer.mark('Sent BeforePublishEvent for %s' % obj.uniqueId)

        new_obj = self.cycle(obj)
        return new_obj

    def after_publish(self, obj, master):
        self.log(obj, _('Published'))
        zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(obj, master))
        timer.mark('Sent PublishedEvent for %s' % obj.uniqueId)
        return obj


@zeit.cms.celery.task(bind=True)
def PUBLISH_TASK(self, ids):
    return PublishTask(self.request.id).run(ids)


class RetractTask(PublishRetractTask):
    """Retract an object."""

    mode = MODE_RETRACT

    def _run(self, objs):
        logger.info('Retracting %s' % ', '.join(obj.uniqueId for obj in objs))
        errors = []
        retracted = []
        for obj in objs:
            info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
            if not info.published:
                logger.warning('Retracting object %s which is not published.', obj.uniqueId)
            try:
                obj = self.recurse(self.before_retract, obj, obj)
            except Exception as e:
                errors.append((obj, e))
            else:
                retracted.append(obj)

        to_retract = []
        for obj in retracted:
            try:
                deps = []
                self.recurse(self.serialize, obj, deps)
                to_retract.extend(reversed(deps))
            except Exception as e:
                errors.append((obj, e))

        try:
            if to_retract:
                publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
                publisher.request(to_retract, self.mode)
        except zeit.workflow.publisher.PublisherError as e:
            errors.extend(self._assign_publisher_errors_to_objects(e, retracted))
        except Exception as e:
            for obj in retracted:
                errors.append((obj, e))

        for obj in retracted:
            try:
                self.recurse(self.after_retract, obj, obj)
            except Exception as e:
                errors.append((obj, e))

        if errors:
            raise MultiPublishError(errors)

        return 'Retracted.'

    def before_retract(self, obj, master):
        """Do things before the actual retract."""
        self.lock(obj)
        zope.event.notify(zeit.cms.workflow.interfaces.BeforeRetractEvent(obj, master))
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = False
        self.log(obj, _('Retracted'))
        return obj

    def after_retract(self, obj, master):
        """Do things after retract."""
        zope.event.notify(zeit.cms.workflow.interfaces.RetractedEvent(obj, master))
        obj = self.cycle(obj)
        self.unlock(obj)
        return obj

    @property
    def repository(self):
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)


@zeit.cms.celery.task(bind=True)
def RETRACT_TASK(self, ids):
    return RetractTask(self.request.id).run(ids)


class MultiTask:
    def run(self, ids):
        self.context = zeit.cms.interfaces.ICMSContent(ids.pop(0), None)
        return super().run(ids)

    def _run(self, objs):
        if FEATURE_TOGGLES.find('enable-commit-on-multi-publish'):
            return super()._run(objs)
        self._to_log = []
        result = super()._run(objs)
        # Work around limitations of our ZODB-based DAV cache.
        # Since publishing a sizeable amount of objects will result in a rather
        # long-running transaction (100 articles take about two minutes), the
        # probability of ConflictErrors is very high there, see ZON-3715 for
        # details. We prevent this by simply not writing to the DAV cache
        # inside the job, which is the only change this commit() would be
        # writing -- since the DAV changes itself happen immediately without
        # transaction isolation anyway. The DAV cache will then be updated
        # shortly afterwards by the invalidator (since that runs for all
        # changes and doesn't discriminate changes made by vivi itself).
        raise z3c.celery.celery.Abort(self._log_messages, self._to_log, message=result)

    def log(self, obj, message):
        if FEATURE_TOGGLES.find('enable-commit-on-multi-publish'):
            super().log(obj, message)
        else:
            self._to_log.append((obj, message))

    def _assign_publisher_error_details(self, exc, objects):
        errors = []
        msg = f'{exc.url} returned {exc.status}'
        by_uuid = {IUUID(x).shortened: x for x in objects}
        for error in exc.errors:
            obj = by_uuid.get(error['source'].get('pointer'))
            if obj is not None:
                errors.append((obj, PublishError.from_detail(msg, error)))
        return errors


class MultiPublishTask(MultiTask, PublishTask):
    """Publish multiple objects"""


@zeit.cms.celery.task(bind=True)
def MULTI_PUBLISH_TASK(self, ids):
    return MultiPublishTask(self.request.id).run(ids)


class MultiRetractTask(MultiTask, RetractTask):
    """Retract multiple objects"""


@zeit.cms.celery.task(bind=True)
def MULTI_RETRACT_TASK(self, ids):
    return MultiRetractTask(self.request.id).run(ids)


class Timer(threading.local):
    def start(self, message):
        self.times = []
        self.mark(message)

    def mark(self, message):
        self.times.append((time.time(), message))

    def get_timings(self):
        result = []
        last = None
        total = 0
        for when, message in self.times:
            if last is None:
                diff = 0
            else:
                diff = when - last
            total += diff
            last = when
            result.append((diff, total, message))
        return result

    def __str__(self):
        result = []
        for diff, total, message in self.get_timings():
            result.append('%2.4f %2.4f %s' % (diff, total, message))
        return '\n'.join(result)


timer = Timer()
