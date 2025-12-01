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
from zeit.cms.content.sources import FEATURE_TOGGLES
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

    def publish_multiple(self, items, priority=PRIORITY_LOW, **kw):
        """Publish multiple objects."""
        if not items:
            logger.warning(
                'Not starting a publishing task, because no objects to publish were given'
            )
            return []
        results = []
        for content in items:
            content = zeit.cms.interfaces.ICMSContent(content)
            self.log(
                content,
                _('Collective Publication of ${count} objects', mapping={'count': len(items)}),
            )

            info = zeit.cms.workflow.interfaces.IPublishInfo(content)
            if info.can_publish() == CAN_PUBLISH_ERROR:
                self.log(content, 'Publish pre-conditions not satisfied.')
                continue
            results.append(
                self._execute_task(
                    PUBLISH_TASK,
                    [content.uniqueId],
                    priority,
                    True,
                    self.context.uniqueId,
                    **kw,
                )
            )
        return results

    def retract_multiple(self, items, priority=PRIORITY_LOW, background=True, **kw):
        """Retract multiple objects."""
        if not items:
            logger.warning('Not starting a retract task, because no objects to retract were given')
            return None
        ids = []
        for content in items:
            content = zeit.cms.interfaces.ICMSContent(content)
            self.log(
                content,
                _('Collective Retraction of ${count} objects', mapping={'count': len(items)}),
            )
            ids.append(content.uniqueId)
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

    def log(self, content, msg):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(content, msg)

    def get_priority(self, priority):
        if priority is None:
            priority = zeit.cms.workflow.interfaces.IPublishPriority(self.context)
        return priority


class MultiPublishError(Exception):
    pass


MODE_PUBLISH = 'publish'
MODE_RETRACT = 'retract'


class Worklist:
    """Manages content to be published/retracted with their dependencies."""

    def __init__(self, all_content, initiating_map):
        #: Dict mapping uniqueId -> content object (includes dependencies)
        self.all_content = all_content
        #: Dict mapping each content's uniqueId to its initiator's uniqueId
        self._initiating_map = initiating_map
        self.errors = []

    @classmethod
    def build(cls, trees_by_content):
        all_content = {}
        initiating_map = {}

        for content, tree in trees_by_content.items():
            for tree_content in tree:
                if tree_content.uniqueId not in all_content:
                    all_content[tree_content.uniqueId] = tree_content
                    # Track which requested content caused this to be added
                    initiating_map[tree_content.uniqueId] = content.uniqueId

        return cls(all_content, initiating_map)

    def snapshot(self):
        """Copy the current state. This is used to unlock all content that was
        locked, regardless of errors that occur further down the line.
        Note that the `errors` list is intentionally shared between snapshots,
        so that we can report all errors, regardless of where they occur.
        """
        result = type(self)(self.all_content.copy(), self.initiating_map)
        result.errors = self.errors
        return result

    def initiating(self, content):
        """Get the initiator (requested content) for given content.

        For requested content, returns itself. For dependencies, returns the first
        requested content that added this dependency to the tree.
        """
        return self.all_content[self._initiating_map[content.uniqueId]]

    def __iter__(self):
        """Return items that should be processed in the current phase."""
        # Need to make a copy to allow for remove() while iterating.
        return iter(list(self.all_content.values()))

    def update(self, content):
        self.all_content[content.uniqueId] = content

    def remove(self, content, error):
        del self.all_content[content.uniqueId]
        self.errors.append((content, error))


class PublishRetractTask:
    mode = NotImplemented  # MODE_PUBLISH or MODE_RETRACT

    def __init__(self, jobid):
        self.jobid = jobid

    def run(self, ids, collect_errors_on=None):
        """Run task in worker."""
        ids_str = ', '.join(ids)
        logger.info('Running job %s for %s', self.jobid, ids_str)

        items = []
        with zeit.cms.tracing.use_span(__name__, 'resolve content'):
            for uniqueId in ids:
                try:
                    items.append(self.repository.getContent(uniqueId))
                except KeyError:
                    logger.warning('Not found %s, ignoring', uniqueId)

        try:
            result = self._run(items)
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
                for content, error in e.args[0]:
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
                    to_log.append((content, submessage))
                    with_error.append(content.uniqueId)
                    all_errors.append(
                        (content, '%s: %s' % (error.__class__.__name__, errormessage))
                    )
                if len(all_errors) == 1:
                    all_errors = all_errors[0][1]
                message = _(messageid, mapping={'exc': '', 'message': str(all_errors)})
            else:
                message = _(messageid, mapping={'exc': e.__class__.__name__, 'message': str(e)})
                to_log = [(content, message) for content in items]
                with_error = [content.uniqueId for content in items]

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

    def _assign_publisher_errors_to_objects(self, exc, items):
        errors = []
        msg = f'{exc.url} returned {exc.status}'
        if not exc.errors:
            e = PublishError(msg)
            for content in items:
                errors.append((content, e))
        elif len(exc.errors) == 1 and not exc.errors[0].get('source'):
            e = PublishError.from_detail(msg, exc.errors[0])
            for content in items:
                errors.append((content, e))
        else:
            errors.extend(self._assign_publisher_error_details(exc, items))
        return errors

    def _assign_publisher_error_details(self, exc, items):
        details = json.dumps(exc.errors)
        e = PublishError(f'{exc.url} returned {exc.status}, Details: {details}')
        errors = []
        for content in items:
            errors.append((content, e))
        return errors

    def _log_messages(self, objs_and_messages):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        for content, message in objs_and_messages:
            log.log(content, message)

    def cycle(self, content):
        """checkout/checkin content to sync data as necessary.

        The basic idea is that there are some event handlers which sync
        properties to xml on checkout/checkin.

        """
        if not zeit.cms.content.interfaces.IXMLContent.providedBy(content):
            return content
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
        try:
            # We do not use the user's workingcopy but a "fresh" one which we
            # just throw away afterwards. This has two effects: 1. The users'
            # workingcopy istn't cluttered with ghosts and 2. we can publish in
            # parallel.
            checked_out = manager.checkout(temporary=True, publishing=True)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            logger.warning('Could not checkout %s' % content.uniqueId)
            return content
        manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
        try:
            return manager.checkin(publishing=True)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # XXX this codepath is not tested!
            logger.warning('Could not checkin %s' % content.uniqueId)
            del checked_out.__parent__[checked_out.__name__]
            return content

    def recurse(self, method, start_obj, *args):
        """Apply method recursively on start_obj (legacy implementation)."""
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
            logger.debug('%s %s' % (method.__name__, current_obj.uniqueId))
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

    def build_dependencies(self, start_content):
        """Queries dependencies before any state changes occur (e.g. published=True)."""
        DEPENDENCY_PUBLISH_LIMIT = int(
            zeit.cms.config.get('zeit.workflow', 'dependency-publish-limit', 1)
        )
        stack = [start_content]
        seen = set()
        result = []

        with zeit.cms.tracing.use_span(
            __name__,
            'build dependencies',
            attributes={'app.uniqueid': start_content.uniqueId, 'app.mode': self.mode},
        ):
            while stack:
                current_content = stack.pop(0)
                if current_content.uniqueId in seen:
                    continue
                seen.add(current_content.uniqueId)
                result.append(current_content)

                if len(seen) > DEPENDENCY_PUBLISH_LIMIT:
                    # "strictly greater" comparison since the starting content
                    # should not count towards the limit
                    break

                # Resolve dependencies before any state changes
                with zeit.cms.tracing.use_span(
                    __name__,
                    'resolve dependencies',
                    attributes={'app.uniqueid': current_content.uniqueId},
                ):
                    deps = zeit.cms.workflow.interfaces.IPublicationDependencies(current_content)
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

    def _execute_phase(self, worklist, phase_name, phase_fn, needs_initiating_content=False):
        result = []
        for content in worklist:
            try:
                logger.debug('%s %s' % (phase_name, content.uniqueId))
                with zeit.cms.tracing.use_span(
                    __name__,
                    phase_name,
                    attributes={'app.uniqueid': content.uniqueId, 'app.mode': self.mode},
                ):
                    params = []
                    if needs_initiating_content:
                        params.append(worklist.initiating(content))
                    value = phase_fn(content, *params)
                    result.append(value)
            except Exception as e:
                worklist.remove(content, e)
        return result

    def _execute_phase_with_content_update(
        self, worklist, phase_name, phase_fn, needs_initiating_content=False
    ):
        # cycle may update content during checkin event (but I really don't know
        # and hopefully we can remove it in the future and skip that check)
        for content in self._execute_phase(
            worklist, phase_name, phase_fn, needs_initiating_content
        ):
            worklist.update(content)

    def serialize(self, content):
        return zeit.workflow.interfaces.IPublisherData(content)(self.mode)

    def serialize_legacy(self, content, result):
        result.append(zeit.workflow.interfaces.IPublisherData(content)(self.mode))

    def log(self, content, message):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(content, message)

    @property
    def repository(self):
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    @staticmethod
    def lock(content):
        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(content.uniqueId))
        lockable = zope.app.locking.interfaces.ILockable(content, None)
        if lockable is not None and not lockable.ownLock():
            if lockable.locked():
                raise zope.app.locking.interfaces.LockingError(
                    _(
                        'The object ${name} is locked by ${user}.',
                        mapping={'name': content.uniqueId, 'user': lockable.locker()},
                    )
                )
            lockable.lock(timeout=240)

    @staticmethod
    def unlock(content):
        lockable = zope.app.locking.interfaces.ILockable(content, None)
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

    def _run(self, items):
        if FEATURE_TOGGLES.find('publish_refactored_worklist'):
            return self._run_new(items)
        else:
            return self._run_legacy(items)

    def _run_new(self, items):
        logger.info('Publishing %s (new)' % ', '.join(content.uniqueId for content in items))

        trees = {content: self.build_dependencies(content) for content in items}
        worklist = Worklist.build(trees)
        self._execute_phase(worklist, 'can_publish', self.can_publish)
        self._execute_phase(worklist, 'lock', self.lock)
        locked = worklist.snapshot()
        # Persist locks as soon as possible, to prevent concurrent access.
        transaction.commit()

        self._execute_phase_with_content_update(
            worklist, 'before_publish', self.before_publish, needs_initiating_content=True
        )

        to_publish = self._execute_phase(worklist, 'serialize', self.serialize)
        try:
            if to_publish:
                # Persist changes before having an external system read them.
                transaction.commit()
                publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
                publisher.request(to_publish, self.mode)
        except transaction.interfaces.TransientError:
            raise
        except zeit.workflow.publisher.PublisherError as e:
            worklist.errors.extend(self._assign_publisher_errors_to_objects(e, list(worklist)))
        except Exception as e:
            for content in worklist:
                worklist.errors.append((content, e))

        self._execute_phase(
            worklist, 'after_publish', self.after_publish, needs_initiating_content=True
        )
        self._execute_phase(locked, 'unlock', self.unlock)

        # No commit here, as it would also commit any after_publish changes.
        # We may leave content locked, if an error occurred, but that's the
        # lesser evil of the two.

        if worklist.errors:
            raise MultiPublishError(worklist.errors)

        return 'Published.'

    def _run_legacy(self, objs):
        logger.info('Publishing %s (legacy)' % ', '.join(obj.uniqueId for obj in objs))
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
                self.recurse(self.serialize_legacy, obj, deps)
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
                self.recurse(self.unlock, obj)
            except Exception as e:
                errors.append((obj, e))
        # No commit here, as it would also commit any after_publish changes.
        # We may leave objects locked, if an error occurred, but that's the
        # lesser evil of the two.

        if errors:
            raise MultiPublishError(errors)

        return 'Published.'

    def can_publish(self, content):
        """at least check if the content can be published before
        setting published to True"""
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        if info.can_publish() == CAN_PUBLISH_ERROR:
            errors = []
            for error_message in info.error_messages:
                errors.append(zope.i18n.translate(error_message, target_language='de'))
            raise zeit.cms.workflow.interfaces.PublishingError(', '.join(errors))

    def can_retract(self, content):
        """at least check if the content can be retracted before
        setting published to True"""
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        if info.can_retract() == CAN_RETRACT_ERROR:
            errors = []
            for error_message in info.error_messages:
                errors.append(zope.i18n.translate(error_message, target_language='de'))
            raise zeit.cms.workflow.interfaces.RetractingError(', '.join(errors))

    def before_publish(self, content, initiator):
        """Do everything necessary before the actual publish."""
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        info.published = True
        info.date_last_published = pendulum.now('UTC')
        if not info.date_first_released:
            info.date_first_released = info.date_last_published

        # XXX Yes this is not strictly _before_ publish. However, zeit.retresco
        # needs this point in time to perform its indexing, and the other
        # subscribers don't care either way, so it's probably not worth
        # introducing two separate events.
        zope.event.notify(zeit.cms.workflow.interfaces.BeforePublishEvent(content, initiator))

        return self.cycle(content)

    def after_publish(self, content, initiator):
        self.log(content, _('Published'))
        zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(content, initiator))


@zeit.cms.celery.task(bind=True)
def PUBLISH_TASK(self, ids, collect_errors_on=None):
    return PublishTask(self.request.id).run(ids, collect_errors_on)


class RetractTask(PublishRetractTask):
    """Retract an object."""

    mode = MODE_RETRACT

    def _run(self, items):
        if FEATURE_TOGGLES.find('publish_refactored_worklist'):
            return self._run_new(items)
        else:
            return self._run_legacy(items)

    def _run_new(self, items):
        logger.info('Retracting %s (new)' % ', '.join(content.uniqueId for content in items))

        for content in items:
            info = zeit.cms.workflow.interfaces.IPublishInfo(content)
            if not info.published:
                logger.warning('Retracting content %s which is not published.', content.uniqueId)

        trees = {content: self.build_dependencies(content) for content in items}
        worklist = Worklist.build(trees)
        self._execute_phase(worklist, 'lock', self.lock)
        locked = worklist.snapshot()
        # Persist locks as soon as possible, to prevent concurrent access.
        transaction.commit()

        self._execute_phase_with_content_update(
            worklist, 'before_retract', self.before_retract, needs_initiating_content=True
        )

        to_retract = self._execute_phase(worklist, 'serialize', self.serialize)
        to_retract.reverse()

        try:
            if to_retract:
                transaction.commit()
                publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
                publisher.request(to_retract, self.mode)
        except transaction.interfaces.TransientError:
            raise
        except zeit.workflow.publisher.PublisherError as e:
            worklist.errors.extend(self._assign_publisher_errors_to_objects(e, list(worklist)))
        except Exception as e:
            for content in worklist:
                worklist.errors.append((content, e))

        self._execute_phase(
            worklist, 'after_retract', self.after_retract, needs_initiating_content=True
        )
        self._execute_phase(locked, 'unlock', self.unlock)

        if worklist.errors:
            raise MultiPublishError(worklist.errors)

        return 'Retracted.'

    def _run_legacy(self, objs):
        logger.info('Retracting %s (legacy)' % ', '.join(obj.uniqueId for obj in objs))

        for obj in objs:
            info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
            if not info.published:
                logger.warning('Retracting object %s which is not published.', obj.uniqueId)

        errors = []
        okay = []
        for obj in objs:
            try:
                okay.append(self.recurse(self.lock, obj))
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
                self.recurse(self.serialize_legacy, obj, deps)
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
                self.recurse(self.unlock, obj)
            except Exception as e:
                errors.append((obj, e))

        if errors:
            raise MultiPublishError(errors)

        return 'Retracted.'

    def before_retract(self, content, initiator):
        zope.event.notify(zeit.cms.workflow.interfaces.BeforeRetractEvent(content, initiator))
        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        info.published = False
        info.date_last_retracted = pendulum.now('UTC')
        self.log(content, _('Retracted'))

    def after_retract(self, content, initiator):
        zope.event.notify(zeit.cms.workflow.interfaces.RetractedEvent(content, initiator))
        return self.cycle(content)


@zeit.cms.celery.task(bind=True)
def RETRACT_TASK(self, ids, collect_errors_on=None):
    return RetractTask(self.request.id).run(ids, collect_errors_on)


class MultiTask:
    def _assign_publisher_error_details(self, exc, items):
        errors = []
        msg = f'{exc.url} returned {exc.status}'
        by_uuid = {IUUID(x).shortened: x for x in items}
        for error in exc.errors:
            content = by_uuid.get(error['source'].get('pointer'))
            if content is not None:
                errors.append((content, PublishError.from_detail(msg, error)))
        return errors


class MultiRetractTask(MultiTask, RetractTask):
    """Retract multiple objects"""


@zeit.cms.celery.task(bind=True)
def MULTI_RETRACT_TASK(self, ids, collect_errors_on=None):
    return MultiRetractTask(self.request.id).run(ids, collect_errors_on)
