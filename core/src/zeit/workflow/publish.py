from __future__ import with_statement
from datetime import datetime
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import PRIORITY_LOW
import ZODB.POSException
import logging
import lovely.remotetask.interfaces
import os.path
import pytz
import random
import subprocess
import tempfile
import threading
import time
import transaction
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.objectlog.interfaces
import zope.app.appsetup.product
import zope.app.security.interfaces
import zope.component
import zope.event
import zope.interface
import zope.publisher.interfaces
import zope.security.management


logger = logging.getLogger(__name__)
timer_logger = logging.getLogger('zeit.workflow.timer')


class Publish(object):

    zope.interface.implements(zeit.cms.workflow.interfaces.IPublish)
    zope.component.adapts(zeit.cms.repository.interfaces.IRepositoryContent)

    def __init__(self, context):
        self.context = context

    def publish(self, priority=None, async=True):
        """Publish object."""
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        if info.can_publish() == CAN_PUBLISH_ERROR:
            raise zeit.cms.workflow.interfaces.PublishingError(
                "Publish pre-conditions not satisifed.")

        if priority is None:
            priority = zeit.cms.workflow.interfaces.IPublishPriority(
                self.context)
        task = u'zeit.workflow.publish'
        if async:
            self.log(self.context, _('Publication scheduled'))
            return self.tasks(priority).add(task, SingleInput(self.context))
        else:
            task = zope.component.getUtility(
                lovely.remotetask.interfaces.ITask, name=task)
            task.run_sync(self.context)

    def retract(self, priority=None, async=True):
        """Retract object."""
        if priority is None:
            priority = zeit.cms.workflow.interfaces.IPublishPriority(
                self.context)
        task = u'zeit.workflow.retract'
        if async:
            self.log(self.context, _('Retracting scheduled'))
            return self.tasks(priority).add(task, SingleInput(self.context))
        else:
            task = zope.component.getUtility(
                lovely.remotetask.interfaces.ITask, name=task)
            task.run_sync(self.context)

    def publish_multiple(self, objects, priority=PRIORITY_LOW, async=True):
        if not objects:
            logger.warning('Not starting a publishing task, because no objects'
                           ' to publish were given')
            return
        ids = []
        for obj in objects:
            obj = zeit.cms.interfaces.ICMSContent(obj)
            self.log(obj, _('Collective Publication'))
            if async:
                ids.append(obj.uniqueId)
            else:
                ids.append(obj)
        task = u'zeit.workflow.publish-multiple'
        if async:
            return self.tasks(priority).add(task, MultiInput(ids))
        else:
            task = zope.component.getUtility(
                lovely.remotetask.interfaces.ITask, name=task)
            task.run_sync(ids)

    def tasks(self, priority):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        queue = config['task-queue-%s' % priority]
        return zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name=queue)

    def log(self, obj, msg):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, msg)


class SingleInput(object):
    """Data to be passed to publish/retract tasks."""

    def __init__(self, obj):
        self.uniqueId = obj.uniqueId
        self.principal = self.get_principal().id

    def resolve(self):
        return self.repository.getContent(self.uniqueId)

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @staticmethod
    def get_principal():
        interaction = zope.security.management.getInteraction()
        for p in interaction.participations:
            return p.principal

    def acquire_active_lock(self):
        return self._acquire_active_lock(self.uniqueId)

    def _acquire_active_lock(self, uniqueId):
        with active_objects_lock:
            if uniqueId in active_objects:
                return False
            active_objects.add(uniqueId)
            return True

    def release_active_lock(self):
        self._release_active_lock(self.uniqueId)

    def _release_active_lock(self, uniqueId):
        with active_objects_lock:
            active_objects.remove(uniqueId)

    def __str__(self):
        return unicode(self).encode('ascii', 'backslashreplace')

    def __unicode__(self):
        return self.uniqueId


# BBB for persistent instances
class TaskDescription(SingleInput):
    pass


class MultiInput(SingleInput):

    def __init__(self, ids):
        self.ids = ids
        self.principal = self.get_principal().id

    def resolve(self):
        return [self.repository.getContent(x) for x in self.ids]

    def acquire_active_lock(self):
        for id in self.ids:
            acquired = self._acquire_active_lock(id)
            if not acquired:
                return False
        return True

    def release_active_lock(self):
        for id in self.ids:
            self._release_active_lock(id)

    def __unicode__(self):
        return unicode(self.ids)


active_objects = set()
active_objects_lock = threading.Lock()

MODE_PUBLISH = 'publish'
MODE_RETRACT = 'retract'


class PublishRetractTask(object):

    zope.interface.implements(lovely.remotetask.interfaces.ITask)
    # inputSchema = zope.schema.Object()  # XXX
    # outputSchema = None or an error message
    mode = NotImplemented  # MODE_PUBLISH or MODE_RETRACT

    def __call__(self, service, jobid, input):
        info = (type(self).__name__, unicode(input), jobid)
        __traceback_info__ = info
        timer.start(u'Job %s started: %s (%s)' % info)
        logger.info("Running job %s" % jobid)

        self.login(input.principal)
        timer.mark('Logged in')

        obj = input.resolve()
        timer.mark('Looked up object')

        retries = 0
        while True:
            try:
                try:
                    acquired = input.acquire_active_lock()
                    if acquired:
                        self.run(obj)
                    else:
                        self.log(
                            obj, _('A publish/retract job is already active.'
                                   ' Aborting'))
                        logger.info(
                            'Aborting parallel publish/retract of %s', input)
                    self.commit()
                    timer.mark('Commited')
                except ZODB.POSException.ConflictError, e:
                    timer.mark('Conflict')
                    retries += 1
                    if retries >= 3:
                        raise
                    # Spiels noch einmal, Sam.
                    logger.warning('Conflict while publishing', exc_info=True)
                    transaction.abort()
                    # Stagger retry:
                    time.sleep(random.uniform(0, 2 ** retries))
                    continue
            except Exception, e:
                transaction.abort()
                logger.error("Error during publish/retract", exc_info=True)
                message = _("Error during publish/retract: ${exc}: ${message}",
                            mapping=dict(
                                exc=e.__class__.__name__,
                                message=str(e)))
                self.log(obj, message)
                break
            else:
                # Everything okay.
                message = None
                break
            finally:
                if acquired:
                    input.release_active_lock()
        timer.mark(u'Done %s' % input)
        timer_logger.debug('Timings:\n%s' % (unicode(timer).encode('utf8'),))
        dummy, total, timer_message = timer.get_timings()[-1]
        logger.info('%s (%2.4fs)' % (timer_message, total))
        return message

    def commit(self):  # Extension point for subclasses
        transaction.commit()

    def run_sync(self, obj):
        timer.start(u'Synchronous %s started: %s' % (
            type(self).__name__, obj))
        self.run(obj)
        timer.mark('Done %s' % obj)
        dummy, total, timer_message = timer.get_timings()[-1]
        logger.info('%s (%2.4fs)' % (timer_message, total))

    def cycle(self, obj):
        """checkout/checkin obj to sync data as necessary.

        The basic idea is that there are some event handlers which sync
        properties to xml on checkout/checkin.

        """
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(obj)
        try:
            # We do not use the user's workingcopy but a "fresh" one which we
            # just throw away afterwards. This has two effects: 1. The users'
            # workingcopy istn't cluttered with ghosts and 2. we can publish in
            # parallel.
            checked_out = manager.checkout(temporary=True, publishing=True)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            logger.warning("Could not checkout %s" % obj.uniqueId)
            return obj
        manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
        try:
            obj = manager.checkin(publishing=True)
        except zeit.cms.checkout.interfaces.CheckinCheckoutError:
            # XXX this codepath is not tested!
            logger.warning("Could not checkin %s" % obj.uniqueId)
            del checked_out.__parent__[checked_out.__name__]
            return obj
        timer.mark('Cycled %s' % obj.uniqueId)
        return obj

    def recurse(self, method, obj, *args):
        """Apply method recursively on obj."""
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        DEPENDENCY_PUBLISH_LIMIT = config['dependency-publish-limit']
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
            timer.mark('Called %s on %s' % (method.__name__,
                                            current_obj.uniqueId))
            if len(seen) > DEPENDENCY_PUBLISH_LIMIT:
                # "strictly greater" comparison since the starting object
                # should not count towards the limit
                break

            # Dive into folders
            if zeit.cms.repository.interfaces.ICollection.providedBy(new_obj):
                stack.extend(new_obj.values())
                timer.mark('Recursed into %s' % (new_obj.uniqueId,))

            # Dive into dependent objects
            deps = zeit.workflow.interfaces.IPublicationDependencies(new_obj)
            if self.mode == MODE_PUBLISH:
                stack.extend(deps.get_dependencies())
            elif self.mode == MODE_RETRACT:
                stack.extend(deps.get_retract_dependencies())
            else:
                raise ValueError('Task mode must be %r or %r, not %r' % (
                    MODE_PUBLISH, MODE_RETRACT, self.mode))
            timer.mark('Got dependencies for %s' % (new_obj.uniqueId,))

            if result_obj is None:
                result_obj = new_obj

        return result_obj

    def get_all_paths(self, obj):
        unique_ids = []
        self.recurse(self.get_unique_id, obj, unique_ids)
        # The publish/retract scripts doesn't want URLs but local paths, so
        # munge them.
        paths = [self.convert_uid_to_path(uid) for uid in unique_ids]
        return paths

    def get_unique_id(self, obj, unique_ids):
        unique_ids.append(obj.uniqueId)
        return obj

    def convert_uid_to_path(self, uid):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        path_prefix = config['path-prefix']
        return os.path.join(
            path_prefix,
            uid.replace(zeit.cms.interfaces.ID_NAMESPACE, '', 1))

    @staticmethod
    def login(principal):
        interaction = zope.security.management.getInteraction()
        participation = interaction.participations[0]
        assert(zope.publisher.interfaces.IPublicationRequest.providedBy(
            participation))
        auth = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication)
        participation.setPrincipal(auth.getPrincipal(principal))

    @property
    def log(self):
        return zope.component.getUtility(
            zeit.objectlog.interfaces.IObjectLog).log

    @staticmethod
    def lock(obj, master=None):
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(obj.uniqueId))
        lockable = zope.app.locking.interfaces.ILockable(obj, None)
        if (lockable is not None and
                not lockable.locked() and
                not lockable.ownLock()):
            lockable.lock(timeout=240)
        timer.mark('Locked %s' % obj.uniqueId)
        return obj

    @staticmethod
    def unlock(obj, master=None):
        lockable = zope.app.locking.interfaces.ILockable(obj, None)
        if (lockable is not None and
                lockable.locked() and
                lockable.ownLock()):
            lockable.unlock()
        timer.mark('Unlocked %s' % obj.uniqueId)
        return obj

    @staticmethod
    def call_script(filename, input_data):
        if isinstance(input_data, unicode):
            input_data = input_data.encode('UTF-8')
        with tempfile.NamedTemporaryFile() as f:
            f.write(input_data)
            f.flush()

            out = tempfile.NamedTemporaryFile()
            err = tempfile.NamedTemporaryFile()
            proc = subprocess.Popen([filename, f.name], stdout=out, stderr=err)
            proc.communicate()
            out.seek(0)
            err.seek(0)
            stdout = out.read()
            stderr = err.read()
            out.close()
            err.close()

            if proc.returncode:
                logger.error("%s exited with %s" % (filename, proc.returncode))
            if stdout:
                logger.info("%s:\n%s" % (filename, stdout))
            if stderr:
                logger.error("%s:\n%s" % (filename, stderr))
            if proc.returncode:
                raise zeit.workflow.interfaces.ScriptError(
                    stderr, proc.returncode)


class PublishTask(PublishRetractTask):
    """Publish object."""

    mode = MODE_PUBLISH

    def run(self, obj):
        logger.info('Publishing %s' % obj.uniqueId)
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        if info.can_publish() == CAN_PUBLISH_ERROR:
            logger.error("Could not publish %s" % obj.uniqueId)
            self.log(
                obj, _("Could not publish because conditions not satisifed."))
            return

        obj = self.recurse(self.lock, obj, obj)
        obj = self.recurse(self.before_publish, obj, obj)
        self.call_publish_script(self.get_all_paths(obj))
        self.recurse(self.after_publish, obj, obj)
        obj = self.recurse(self.unlock, obj, obj)

    def before_publish(self, obj, master):
        """Do everything necessary before the actual publish."""

        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(obj, master))
        timer.mark('Sent BeforePublishEvent for %s' % obj.uniqueId)

        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = True
        info.date_last_published = datetime.now(pytz.UTC)
        timer.mark('Set date_last_published')
        if not info.date_first_released:
            info.date_first_released = info.date_last_published
            timer.mark('Set date_first_releaesd')

        new_obj = self.cycle(obj)
        return new_obj

    def call_publish_script(self, paths):
        """Actually do the publication."""
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        publish_script = config['publish-script']
        self.call_script(publish_script, '\n'.join(paths))
        timer.mark('Called publish script')

    def after_publish(self, obj, master):
        self.log(obj, _('Published'))
        zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(
            obj, master))
        timer.mark('Sent PublishedEvent for %s' % obj.uniqueId)
        return obj


class RetractTask(PublishRetractTask):
    """Retract an object."""

    mode = MODE_RETRACT

    def run(self, obj):
        logger.info('Retracting %s' % obj.uniqueId)
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        if not info.published:
            logger.warning(
                "Retracting object %s which is not published." % obj.uniqueId)

        obj = self.recurse(self.before_retract, obj, obj)
        self.call_retract_script(obj)
        self.recurse(self.after_retract, obj, obj)

    def before_retract(self, obj, master):
        """Do things before the actual retract."""
        self.lock(obj)
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforeRetractEvent(obj, master))
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = False
        self.log(obj, _('Retracted'))
        return obj

    def call_retract_script(self, obj):
        """Call the script. This does the actual retract."""
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        retract_script = config['retract-script']
        paths = reversed(self.get_all_paths(obj))
        self.call_script(retract_script, '\n'.join(paths))

    def after_retract(self, obj, master):
        """Do things after retract."""
        zope.event.notify(zeit.cms.workflow.interfaces.RetractedEvent(
            obj, master))
        obj = self.cycle(obj)
        self.unlock(obj)
        return obj

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class MultiPublishTask(PublishTask):
    """Publish multiple objects"""

    def run(self, objects):
        logger.info('Publishing %s', objects)

        published = []
        for obj in objects:
            info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
            if info.can_publish() == CAN_PUBLISH_ERROR:
                logger.error("Skipping %s", obj.uniqueId)
                self.log(obj, _(
                    "Could not publish because conditions not satisifed."))
                continue

            obj = self.recurse(self.lock, obj, obj)
            obj = self.recurse(self.before_publish, obj, obj)
            published.append(obj)

        paths = []
        for obj in published:
            paths.extend(self.get_all_paths(obj))
        self.call_publish_script(paths)

        for obj in published:
            self.recurse(self.after_publish, obj, obj)
            obj = self.recurse(self.unlock, obj, obj)

    def commit(self):
        # Work around limitations of our ZODB-based DAV cache.
        # Since publishing a sizable amount of objects will result in a rather
        # long-running transaction (100 articles take about two minutes), the
        # probability of ConflictErrors is very high there, see ZON-3715 for
        # details. We prevent this by simply not writing to the DAV cache
        # inside the job, which is the only change this commit() would be
        # writing -- since the DAV changes itself happen immediately without
        # transaction isolation anyway. The DAV cache will then be updated
        # shortly afterwards by the invalidator (since that runs for all
        # changes and doesn't discriminate changes made by vivi itself).
        transaction.abort()


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

    def __unicode__(self):
        result = []
        for diff, total, message in self.get_timings():
            result.append(u'%2.4f %2.4f %s' % (diff, total, message))
        return u'\n'.join(result)


timer = Timer()
