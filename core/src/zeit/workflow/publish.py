from celery import shared_task
from datetime import datetime
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
import logging
import os.path
import pytz
import subprocess
import tempfile
import threading
import time
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
import zope.i18n
import zope.interface
import zope.publisher.interfaces
import zope.security.management


logger = logging.getLogger(__name__)
timer_logger = logging.getLogger('zeit.workflow.timer')


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

        if async:
            self.log(self.context, _('Publication scheduled'))
            return PUBLISH_TASK.apply_async(
                (self.context.uniqueId,), urgency=self.get_urgency(priority))
        else:
            PUBLISH_TASK(self.context.uniqueId)

    def retract(self, priority=None, async=True):
        """Retract object."""
        if async:
            self.log(self.context, _('Retracting scheduled'))
            return RETRACT_TASK.apply_async(
                (self.context.uniqueId,), urgency=self.get_urgency(priority))
        else:
            RETRACT_TASK(self.context.uniqueId)

    def log(self, obj, msg):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, msg)

    def get_urgency(self, priority):
        if priority is None:
            priority = zeit.cms.workflow.interfaces.IPublishPriority(
                self.context)
        return priority


class PublishRetractTask(object):

    def __init__(self, jobid):
        self.jobid = jobid

    def run(self, uniqueId):
        info = (type(self).__name__, uniqueId, self.jobid)
        __traceback_info__ = info
        timer.start(u'Job %s started: %s (%s)' % info)
        logger.info("Running job %s", self.jobid)

        obj = self.repository.getContent(uniqueId)
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        timer.mark('Looked up object')

        try:
            result = self._run(obj, info)
        except Exception as e:
            logger.error("Error during publish/retract", exc_info=True)
            error_message = _(
                "Error during publish/retract: ${exc}: ${message}",
                mapping=dict(exc=e.__class__.__name__, message=str(e)))
            self.log(obj, error_message)
            self._log_timer(uniqueId)
            raise RuntimeError(zope.i18n.translate(error_message))
        self._log_timer(uniqueId)
        return result

    def _log_timer(self, uniqueId):
        timer.mark('Done %s' % uniqueId)
        timer_logger.debug('Timings:\n%s' % (unicode(timer).encode('utf8'),))
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

    def recurse(self, method, dependencies, obj, *args):
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

            if dependencies:
                # Dive into dependent objects
                deps = zeit.workflow.interfaces.IPublicationDependencies(
                    new_obj)
                stack.extend(deps.get_dependencies())
                timer.mark('Got dependencies for %s' % (new_obj.uniqueId,))

            if result_obj is None:
                result_obj = new_obj

        return result_obj

    def get_all_paths(self, obj, dependencies):
        unique_ids = []
        self.recurse(self.get_unique_id, dependencies, obj, unique_ids)
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

    @property
    def log(self):
        return zope.component.getUtility(
            zeit.objectlog.interfaces.IObjectLog).log

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

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

    def _run(self, obj, info):
        logger.info('Publishing %s' % obj.uniqueId)
        if info.can_publish() == CAN_PUBLISH_ERROR:
            logger.error("Could not publish %s" % obj.uniqueId)
            self.log(
                obj, _("Could not publish because conditions not satisifed."))
            return "Could not publish because conditions not satisfied."

        obj = self.recurse(self.lock, True, obj, obj)
        obj = self.recurse(self.before_publish, True, obj, obj)
        self.call_publish_script(obj)
        self.recurse(self.after_publish, True, obj, obj)
        obj = self.recurse(self.unlock, True, obj, obj)
        return "Published."

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

    def call_publish_script(self, obj):
        """Actually do the publication."""
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        publish_script = config['publish-script']
        paths = self.get_all_paths(obj, True)
        self.call_script(publish_script, '\n'.join(paths))
        timer.mark('Called publish script')

    def after_publish(self, obj, master):
        self.log(obj, _('Published'))
        zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(
            obj, master))
        timer.mark('Sent PublishedEvent for %s' % obj.uniqueId)
        return obj


@shared_task(bind=True)
def PUBLISH_TASK(self, uniqueId):
    return PublishTask(self.task_id).run(uniqueId)


class RetractTask(PublishRetractTask):
    """Retract an object."""

    def _run(self, obj, info):
        logger.info('Retracting %s' % obj.uniqueId)
        if not info.published:
            logger.warning(
                "Retracting object %s which is not published." % obj.uniqueId)

        obj = self.recurse(self.before_retract, False, obj, obj)
        self.call_retract_script(obj)
        self.recurse(self.after_retract, False, obj, obj)
        return "Retracted."

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
        paths = reversed(self.get_all_paths(obj, False))
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


@shared_task(bind=True)
def RETRACT_TASK(self, uniqueId):
    return RetractTask(self.task_id).run(uniqueId)
