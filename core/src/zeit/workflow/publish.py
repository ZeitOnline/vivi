import json
import logging

import celery.result
import celery.states
import pendulum
import transaction
import transaction.interfaces
import z3c.celery.celery
import zope.component
import zope.event
import zope.i18n
import zope.interface

from zeit.cms.content.interfaces import IUUID
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR, CAN_RETRACT_ERROR, PRIORITY_LOW
import zeit.cms.celery
import zeit.cms.checkout.interfaces
import zeit.cms.config
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.tracing
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.objectlog.interfaces
import zeit.workflow.publisher


logger = logging.getLogger(__name__)


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
            message=_('Publication scheduled'),
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
            message=_('Retracting scheduled'),
            **kw,
        )

    def publish_multiple(self, objects, priority=PRIORITY_LOW, **kw):
        """Publish multiple objects."""
        if not objects:
            logger.warning(
                'Not starting a publishing task, because no objects to publish were given'
            )
            return []
        results = []
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.log(
                obj,
                _('Collective Publication of ${count} objects', mapping={'count': len(objects)}),
            )

            info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
            if info.can_publish() == CAN_PUBLISH_ERROR:
                self.log(obj, 'Publish pre-conditions not satisfied.')
                continue
            results.append(
                self._execute_task(
                    PUBLISH_TASK,
                    [obj.uniqueId],
                    priority,
                    True,
                    self.context.uniqueId,
                    **kw,
                )
            )
        return results

    def retract_multiple(self, objects, priority=PRIORITY_LOW, background=True, **kw):
        """Retract multiple objects."""
        if not objects:
            logger.warning('Not starting a retract task, because no objects to retract were given')
            return None
        ids = []
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.log(
                obj, _('Collective Retraction of ${count} objects', mapping={'count': len(objects)})
            )
            ids.append(obj.uniqueId)
        return self._execute_task(
            MULTI_RETRACT_TASK,
            ids,
            priority,
            background,
            self.context.uniqueId,
            **kw,
        )

    def _execute_task(
        self, task, ids, priority, background, collect_errors_on=None, message=None, **kw
    ):
        """`collect_errors_on` is an addtional target for objectlog error messages if given"""
        if background:
            if message:
                self.log(self.context, message)
            return task.apply_async(
                (ids, collect_errors_on), queue=self.get_priority(priority), **kw
            )
        else:
            tracer = zope.component.getUtility(zeit.cms.interfaces.ITracer)
            with tracer.start_as_current_span(
                f'run_sync/{task.name}', attributes={'celery.args': str((ids, collect_errors_on))}
            ):
                result = task(ids, collect_errors_on)
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

    def run(self, ids, collect_errors_on=None):
        """Run task in worker."""
        ids_str = ', '.join(ids)
        info = (type(self).__name__, ids_str, self.jobid)
        __traceback_info__ = info
        logger.info('Running job %s for %s', self.jobid, ids_str)

        objs = []
        with zeit.cms.tracing.use_span(__name__, 'resolve content'):
            for uniqueId in ids:
                try:
                    objs.append(self.repository.getContent(uniqueId))
                except KeyError:
                    logger.warning('Not found %s, ignoring', uniqueId)

        try:
            result = self._run(objs)
        except transaction.interfaces.TransientError:
            raise
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

            if log_target := zeit.cms.interfaces.ICMSContent(collect_errors_on, None):
                to_log.append(
                    (
                        log_target,
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
            return manager.checkin(publishing=True)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # XXX this codepath is not tested!
            logger.warning('Could not checkin %s' % obj.uniqueId)
            del checked_out.__parent__[checked_out.__name__]
            return obj
        return obj

    def recurse(self, method, start_obj, *args):
        """Apply method recursively on start_obj."""
        DEPENDENCY_PUBLISH_LIMIT = int(
            zeit.cms.config.get('zeit.workflow', 'dependency-publish-limit', 1)
        )
        stack = [start_obj]
        seen = set()
        result = None
        while stack:
            current_obj = stack.pop(0)
            if current_obj.uniqueId in seen:
                continue
            seen.add(current_obj.uniqueId)
            logger.debug('%s %s' % (method, current_obj.uniqueId))
            with zeit.cms.tracing.use_span(
                __name__,
                f'publish {method.__name__}',
                attributes={'app.uniqueid': current_obj.uniqueId},
            ):
                new_obj = method(current_obj, *args)
            if new_obj is None:
                new_obj = current_obj
            if result is None:  # Return possible update for start_obj
                result = new_obj
            if len(seen) > DEPENDENCY_PUBLISH_LIMIT:
                # "strictly greater" comparison since the starting object
                # should not count towards the limit
                break

            # Dive into dependent objects
            with zeit.cms.tracing.use_span(
                __name__,
                'resolve dependencies',
                attributes={'app.uniqueid': current_obj.uniqueId, 'app.operation': method.__name__},
            ):
                deps = zeit.cms.workflow.interfaces.IPublicationDependencies(new_obj)
                if self.mode == MODE_PUBLISH:
                    stack.extend(deps.get_dependencies())
                elif self.mode == MODE_RETRACT:
                    stack.extend(deps.get_retract_dependencies())
                else:
                    raise ValueError(
                        'Task mode must be %r or %r, not %r'
                        % (MODE_PUBLISH, MODE_RETRACT, self.mode)
                    )

        return result

    def serialize(self, obj, result):
        result.append(zeit.workflow.interfaces.IPublisherData(obj)(self.mode))

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

    @staticmethod
    def unlock(obj, master=None):
        lockable = zope.app.locking.interfaces.ILockable(obj, None)
        if lockable is not None and lockable.locked() and lockable.ownLock():
            lockable.unlock()


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

        okay = []
        for obj in objs:
            try:
                okay.append(self.recurse(self.can_publish, obj))
            except Exception as e:
                errors.append((obj, e))

        objs = okay
        okay = []
        for obj in objs:
            try:
                okay.append(self.recurse(self.lock, obj))
            except Exception as e:
                errors.append((obj, e))
        locked = okay
        # Persist locks as soon as possible, to prevent concurrent access.
        transaction.commit()

        objs = okay
        okay = []
        for obj in objs:
            try:
                okay.append(self.recurse(self.before_publish, obj, obj))
            except Exception as e:
                errors.append((obj, e))

        to_publish = []
        for obj in okay:
            try:
                deps = []
                self.recurse(self.serialize, obj, deps)
                to_publish.extend(deps)
            except Exception as e:
                errors.append((obj, e))

        try:
            if to_publish:
                # Persist changes before having an external system read them.
                transaction.commit()
                publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
                publisher.request(to_publish, self.mode)
        except transaction.interfaces.TransientError:
            raise
        except zeit.workflow.publisher.PublisherError as e:
            errors.extend(self._assign_publisher_errors_to_objects(e, okay))
        except Exception as e:
            for obj in okay:
                errors.append((obj, e))

        for obj in okay:
            try:
                self.recurse(self.after_publish, obj, obj)
            except Exception as e:
                errors.append((obj, e))

        for obj in locked:
            try:
                self.recurse(self.unlock, obj, obj)
            except Exception as e:
                errors.append((obj, e))
        # No commit here, as it would also commit any after_publish changes.
        # We may leave objects locked, if an error occurred, but that's the
        # lesser evil of the two.

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

    def can_retract(self, obj):
        """at least check if the object can be retracted before
        setting published to True"""
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        if info.can_retract() == CAN_RETRACT_ERROR:
            errors = []
            for error_message in info.error_messages:
                errors.append(zope.i18n.translate(error_message, target_language='de'))
            raise zeit.cms.workflow.interfaces.RetractingError(', '.join(errors))

    def before_publish(self, obj, master):
        """Do everything necessary before the actual publish."""
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = True
        info.date_last_published = pendulum.now('UTC')
        if not info.date_first_released:
            info.date_first_released = info.date_last_published

        # XXX Yes this is not strictly _before_ publish. However, zeit.retresco
        # needs this point in time to perform its indexing, and the other
        # subscribers don't care either way, so it's probably not worth
        # introducing two separate events.
        zope.event.notify(zeit.cms.workflow.interfaces.BeforePublishEvent(obj, master))

        return self.cycle(obj)

    def after_publish(self, obj, master):
        self.log(obj, _('Published'))
        zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(obj, master))


@zeit.cms.celery.task(bind=True)
def PUBLISH_TASK(self, ids, collect_errors_on=None):
    return PublishTask(self.request.id).run(ids, collect_errors_on)


class RetractTask(PublishRetractTask):
    """Retract an object."""

    mode = MODE_RETRACT

    def _run(self, objs):
        logger.info('Retracting %s' % ', '.join(obj.uniqueId for obj in objs))
        errors = []

        okay = []
        for obj in objs:
            info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
            if not info.published:
                logger.warning('Retracting object %s which is not published.', obj.uniqueId)
            try:
                okay.append(self.recurse(self.lock, obj, obj))
            except Exception as e:
                errors.append((obj, e))
        locked = okay
        transaction.commit()

        objs = okay
        okay = []
        for obj in objs:
            try:
                okay.append(self.recurse(self.before_retract, obj, obj))
            except Exception as e:
                errors.append((obj, e))

        to_retract = []
        for obj in okay:
            try:
                deps = []
                self.recurse(self.serialize, obj, deps)
                to_retract.extend(reversed(deps))
            except Exception as e:
                errors.append((obj, e))

        try:
            if to_retract:
                transaction.commit()
                publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
                publisher.request(to_retract, self.mode)
        except transaction.interfaces.TransientError:
            raise
        except zeit.workflow.publisher.PublisherError as e:
            errors.extend(self._assign_publisher_errors_to_objects(e, okay))
        except Exception as e:
            for obj in okay:
                errors.append((obj, e))

        for obj in okay:
            try:
                self.recurse(self.after_retract, obj, obj)
            except Exception as e:
                errors.append((obj, e))

        for obj in locked:
            try:
                self.recurse(self.unlock, obj, obj)
            except Exception as e:
                errors.append((obj, e))

        if errors:
            raise MultiPublishError(errors)

        return 'Retracted.'

    def before_retract(self, obj, master):
        zope.event.notify(zeit.cms.workflow.interfaces.BeforeRetractEvent(obj, master))
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = False
        self.log(obj, _('Retracted'))

    def after_retract(self, obj, master):
        zope.event.notify(zeit.cms.workflow.interfaces.RetractedEvent(obj, master))
        return self.cycle(obj)

    @property
    def repository(self):
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)


@zeit.cms.celery.task(bind=True)
def RETRACT_TASK(self, ids, collect_errors_on=None):
    return RetractTask(self.request.id).run(ids, collect_errors_on)


class MultiTask:
    def _assign_publisher_error_details(self, exc, objects):
        errors = []
        msg = f'{exc.url} returned {exc.status}'
        by_uuid = {IUUID(x).shortened: x for x in objects}
        for error in exc.errors:
            obj = by_uuid.get(error['source'].get('pointer'))
            if obj is not None:
                errors.append((obj, PublishError.from_detail(msg, error)))
        return errors


class MultiRetractTask(MultiTask, RetractTask):
    """Retract multiple objects"""


@zeit.cms.celery.task(bind=True)
def MULTI_RETRACT_TASK(self, ids, collect_errors_on=None):
    return MultiRetractTask(self.request.id).run(ids, collect_errors_on)
