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


class PublishContext:
    """Encapsulates state for publish/retract operations."""

    def __init__(self, all_content, requested_content):
        #: Dict mapping uniqueId -> content object (includes dependencies)
        self.all_content = all_content
        #: Set of uniqueIds that were explicitly requested
        self.requested_content = requested_content
        #: Content still valid to process
        self.processable_content = set(all_content.keys())
        self.errors = []
        self._initiating_cache = {}

    def get_initiating_content(self, uid):
        if uid not in self._initiating_cache:
            if uid in self.requested_content:
                self._initiating_cache[uid] = self.all_content[uid]
            else:
                # For dependencies, initiating content is the first requested object
                self._initiating_cache[uid] = self.all_content[next(iter(self.requested_content))]
        return self._initiating_cache[uid]


class PublishRetractTask:
    mode = NotImplemented  # MODE_PUBLISH or MODE_RETRACT

    def __init__(self, jobid):
        self.jobid = jobid

    def run(self, ids, collect_errors_on=None):
        """Run task in worker."""
        ids_str = ', '.join(ids)
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

    def build_dependency_tree(self, start_obj):
        """Queries dependencies before any state changes occur (e.g. published=True)."""
        DEPENDENCY_PUBLISH_LIMIT = int(
            zeit.cms.config.get('zeit.workflow', 'dependency-publish-limit', 1)
        )
        stack = [start_obj]
        seen = set()
        result = []

        with zeit.cms.tracing.use_span(
            __name__,
            'build dependency tree',
            attributes={'app.uniqueid': start_obj.uniqueId, 'app.mode': self.mode},
        ):
            while stack:
                current_obj = stack.pop(0)
                if current_obj.uniqueId in seen:
                    continue
                seen.add(current_obj.uniqueId)
                result.append(current_obj)

                if len(seen) > DEPENDENCY_PUBLISH_LIMIT:
                    # "strictly greater" comparison since the starting object
                    # should not count towards the limit
                    break

                # Resolve dependencies before any state changes
                with zeit.cms.tracing.use_span(
                    __name__,
                    'resolve dependencies',
                    attributes={'app.uniqueid': current_obj.uniqueId},
                ):
                    deps = zeit.cms.workflow.interfaces.IPublicationDependencies(current_obj)
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

    def _execute_phase(self, ctx, phase_name, phase_fn, needs_initiating_content=False):
        for uid in list(ctx.processable_content):
            content = ctx.all_content[uid]
            try:
                logger.debug('%s %s' % (phase_name, content.uniqueId))
                with zeit.cms.tracing.use_span(
                    __name__,
                    f'{self.mode} {phase_name}',
                    attributes={'app.uniqueid': content.uniqueId},
                ):
                    if needs_initiating_content:
                        initiating_content = ctx.get_initiating_content(uid)
                        new_content = phase_fn(content, initiating_content)
                    else:
                        new_content = phase_fn(content)

                    # cycle may update content during checkin event (but I really don't know
                    # and hopefully we can remove it in the future and skip that check)
                    if new_content is not None and new_content is not content:
                        ctx.all_content[uid] = new_content
            except Exception as e:
                ctx.errors.append((content, e))
                ctx.processable_content.discard(uid)

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

        all_content = {}
        requested_content = set()
        for content in objs:
            requested_content.add(content.uniqueId)
            tree = self.build_dependency_tree(content)
            for tree_content in tree:
                if tree_content.uniqueId not in all_content:
                    all_content[tree_content.uniqueId] = tree_content

        ctx = PublishContext(all_content, requested_content)
        self._execute_phase(ctx, 'can_publish', self.can_publish, needs_initiating_content=False)
        self._execute_phase(ctx, 'lock', self.lock, needs_initiating_content=False)
        locked_content = list(ctx.processable_content)
        # Persist locks as soon as possible, to prevent concurrent access.
        transaction.commit()

        self._execute_phase(
            ctx, 'before_publish', self.before_publish, needs_initiating_content=True
        )

        to_publish = []
        for uid in list(ctx.processable_content):
            content = ctx.all_content[uid]
            try:
                logger.debug('serialize %s' % content.uniqueId)
                with zeit.cms.tracing.use_span(
                    __name__,
                    f'{self.mode} serialize',
                    attributes={'app.uniqueid': content.uniqueId},
                ):
                    self.serialize(content, to_publish)
            except Exception as e:
                ctx.errors.append((content, e))
                ctx.processable_content.discard(uid)

        try:
            if to_publish:
                # Persist changes before having an external system read them.
                transaction.commit()
                publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
                publisher.request(to_publish, self.mode)
        except transaction.interfaces.TransientError:
            raise
        except zeit.workflow.publisher.PublisherError as e:
            ctx.errors.extend(
                self._assign_publisher_errors_to_objects(
                    e, [ctx.all_content[uid] for uid in ctx.processable_content]
                )
            )
        except Exception as e:
            for uid in ctx.processable_content:
                ctx.errors.append((ctx.all_content[uid], e))

        self._execute_phase(ctx, 'after_publish', self.after_publish, needs_initiating_content=True)
        for uid in locked_content:
            if uid not in ctx.all_content:
                logger.warning(
                    'Content %s was locked but not found in all_content during unlock', uid
                )
                continue
            content = ctx.all_content[uid]
            initiating_content = ctx.get_initiating_content(uid)
            try:
                logger.debug('unlock %s' % content.uniqueId)
                with zeit.cms.tracing.use_span(
                    __name__,
                    f'{self.mode} unlock',
                    attributes={'app.uniqueid': content.uniqueId},
                ):
                    self.unlock(content, initiating_content)
            except Exception as e:
                # Don't fail the whole operation if unlock fails, but track the error
                ctx.errors.append((content, e))

        # No commit here, as it would also commit any after_publish changes.
        # We may leave content locked, if an error occurred, but that's the
        # lesser evil of the two.

        if ctx.errors:
            raise MultiPublishError(ctx.errors)

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

        all_content = {}
        requested_content = set()
        for content in objs:
            info = zeit.cms.workflow.interfaces.IPublishInfo(content)
            if not info.published:
                logger.warning('Retracting content %s which is not published.', content.uniqueId)
            requested_content.add(content.uniqueId)
            tree = self.build_dependency_tree(content)
            for tree_content in tree:
                if tree_content.uniqueId not in all_content:
                    all_content[tree_content.uniqueId] = tree_content

        ctx = PublishContext(all_content, requested_content)
        self._execute_phase(ctx, 'lock', self.lock, needs_initiating_content=False)
        locked_content = list(ctx.processable_content)
        # Persist locks as soon as possible, to prevent concurrent access.
        transaction.commit()

        self._execute_phase(
            ctx, 'before_retract', self.before_retract, needs_initiating_content=True
        )

        to_retract = []
        for uid in list(ctx.processable_content):
            content = ctx.all_content[uid]
            try:
                logger.debug('serialize %s' % content.uniqueId)
                with zeit.cms.tracing.use_span(
                    __name__,
                    f'{self.mode} serialize',
                    attributes={'app.uniqueid': content.uniqueId},
                ):
                    self.serialize(content, to_retract)
            except Exception as e:
                ctx.errors.append((content, e))
                ctx.processable_content.discard(uid)

        to_retract = list(reversed(to_retract))

        try:
            if to_retract:
                transaction.commit()
                publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
                publisher.request(to_retract, self.mode)
        except transaction.interfaces.TransientError:
            raise
        except zeit.workflow.publisher.PublisherError as e:
            ctx.errors.extend(
                self._assign_publisher_errors_to_objects(
                    e, [ctx.all_content[uid] for uid in ctx.processable_content]
                )
            )
        except Exception as e:
            for uid in ctx.processable_content:
                ctx.errors.append((ctx.all_content[uid], e))

        self._execute_phase(ctx, 'after_retract', self.after_retract, needs_initiating_content=True)

        for uid in locked_content:
            if uid not in ctx.all_content:
                logger.warning(
                    'Content %s was locked but not found in all_content during unlock', uid
                )
                continue
            content = ctx.all_content[uid]
            initiating_content = ctx.get_initiating_content(uid)
            try:
                logger.debug('unlock %s' % content.uniqueId)
                with zeit.cms.tracing.use_span(
                    __name__,
                    f'{self.mode} unlock',
                    attributes={'app.uniqueid': content.uniqueId},
                ):
                    self.unlock(content, initiating_content)
            except Exception as e:
                ctx.errors.append((content, e))

        if ctx.errors:
            raise MultiPublishError(ctx.errors)

        return 'Retracted.'

    def before_retract(self, obj, master):
        zope.event.notify(zeit.cms.workflow.interfaces.BeforeRetractEvent(obj, master))
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = False
        info.date_last_retracted = pendulum.now('UTC')
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
