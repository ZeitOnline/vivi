# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Publish and retract actions."""

from __future__ import with_statement
from zeit.cms.i18n import MessageFactory as _
import ZODB.POSException
import datetime
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
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workingcopy.workingcopy
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


PUBLISHED_FUTURE_SHIFT = 60


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


class TaskDescription(object):
    """Data to be passed to publish/retract tasks."""

    def __init__(self, obj):
        self.uniqueId = obj.uniqueId
        self.principal = self.get_principal().id

    @staticmethod
    def get_principal():
        interaction = zope.security.management.getInteraction()
        for p in interaction.participations:
            return p.principal


class Publish(object):

    zope.interface.implements(zeit.cms.workflow.interfaces.IPublish)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    def __init__(self, context):
        self.context = context

    def publish(self):
        """Publish object."""
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        if not info.can_publish():
            raise zeit.cms.workflow.interfaces.PublishingError(
                "Publish pre-conditions not satisifed.")

        self.log(self.context, _('Publication scheduled'))
        return self.tasks.add(u'zeit.workflow.publish',
                       TaskDescription(self.context))

    def retract(self):
        """Retract object."""
        self.log(self.context, _('Retracting scheduled'))
        return self.tasks.add(u'zeit.workflow.retract',
                       TaskDescription(self.context))

    @property
    def tasks(self):
        return zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')

    def log(self, obj, msg):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, msg)


active_objects = set()
active_objects_lock = threading.Lock()


class PublishRetractTask(object):

    zope.interface.implements(lovely.remotetask.interfaces.ITask)
    #inputSchema = zope.schema.Object()  # XXX
    #outputSchema = None or an error message

    def __call__(self, service, jobid, input):
        info = (type(self).__name__, input.uniqueId, jobid)
        __traceback_info__ = info
        timer.start(u'Job %s started: %s (%s)' % info)
        logger.info("Running job %s" % jobid)
        uniqueId = input.uniqueId
        principal = input.principal

        self.login(principal)
        timer.mark('Logged in')

        obj = self.repository.getContent(input.uniqueId)
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        timer.mark('Looked up object')

        retries = 0
        while True:
            try:
                try:
                    acquired = self.acquire_active_lock(uniqueId)
                    if acquired:
                        self.run(obj, info)
                    else:
                        self.log(
                            obj, _('A publish/retract job is already active.'
                                   ' Aborting'))
                        logger.info("Aborting parallel publish/retract of %r"
                                    % uniqueId)
                    transaction.commit()
                    timer.mark('Commited')
                except ZODB.POSException.ConflictError, e:
                    timer.mark('Conflict')
                    retries += 1
                    if retries >= 3:
                        raise
                    # Spiels noch einmal, Sam.
                    logger.warning('Conflict while publisheing', exc_info=True)
                    transaction.abort()
                    # Stagger retry:
                    time.sleep(random.uniform(0, 2**(retries)))
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
                    self.release_active_lock(uniqueId)
        timer.mark('Done %s' % input.uniqueId)
        timer_logger.debug('Timings:\n%s' % (unicode(timer).encode('utf8'),))
        dummy, total, timer_message = timer.get_timings()[-1]
        logger.info('%s (%2.4fs)' % (timer_message, total))
        return message

    def acquire_active_lock(self, uniqueId):
        with active_objects_lock:
            if uniqueId in active_objects:
                return False
            active_objects.add(uniqueId)
            return True

    def release_active_lock(self, uniqueId):
        with active_objects_lock:
            active_objects.remove(uniqueId)

    def cycle(self, obj):
        """checkout/checkin obj to sync data as necessary.

        The basic idea is that there are some event handlers which sync
        properties to xml on checkout/checkin.

        """
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(obj)
        if not manager.canCheckout:
            logger.warning("Could not checkout %s" % obj.uniqueId)
            return obj

        # We do not use the user's workingcopy but a "fresh" one which we just
        # throw away afterwards. This has two effects: 1. The users'
        # workingcopy istn't cluttered with ghosts and 2. we can publish in
        # parallel.
        checked_out = manager.checkout(temporary=True)

        manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
        if not manager.canCheckin:
            # XXX this codepath is not tested!
            logger.warning("Could not checkin %s" % obj.uniqueId)
            del checked_out.__parent__[checked_out.__name__]
            return obj
        obj = manager.checkin()
        timer.mark('Cycled %s' % obj.uniqueId)
        return obj

    def recurse(self, method, dependencies, obj, *args):
        """Apply method recursively on obj."""
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

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @staticmethod
    def lock(obj, master=None):
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvaliatedEvent(obj.uniqueId))
        lockable = zope.app.locking.interfaces.ILockable(obj, None)
        if (lockable is not None
            and not lockable.locked()
            and not lockable.ownLock()):
            lockable.lock(timeout=240)
        timer.mark('Locked %s' % obj.uniqueId)
        return obj

    @staticmethod
    def unlock(obj, master=None):
        lockable = zope.app.locking.interfaces.ILockable(obj, None)
        if (lockable is not None
            and lockable.locked()
            and lockable.ownLock()):
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
            proc = subprocess.Popen(
                [filename, f.name],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
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

    def run(self, obj, info):
        logger.info('Publishing %s' % obj.uniqueId)
        if not info.can_publish():
            logger.error("Could not publish %s" % obj.uniqueId)
            self.log(
                obj, _("Could not publish because conditions not satisifed."))
            return


        obj = self.recurse(self.lock, True, obj, obj)
        obj = self.recurse(self.before_publish, True, obj, obj)
        self.call_publish_script(obj)
        self.recurse(self.after_publish, True, obj, obj)
        obj = self.recurse(self.unlock, True, obj, obj)

    def before_publish(self, obj, master):
        """Do everything necessary before the actual publish."""

        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(obj, master))
        timer.mark('Sent BeforePublishEvent for %s' % obj.uniqueId)

        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = True
        # ARGH. This is evil. We need to put the publish time a few seconds
        # into the future to be *after* the cycle call below. During the cycle
        # the object will be most likely changed. It therefore would have a
        # modification after the publication and would be shown as stale in the
        # CMS.
        now = datetime.datetime.now(pytz.UTC) + datetime.timedelta(
            seconds=PUBLISHED_FUTURE_SHIFT)
        info.date_last_published = now
        timer.mark('Set date_last_published')
        if not info.date_first_released:
            info.date_first_released = now
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


class RetractTask(PublishRetractTask):
    """Retract an object."""

    def run(self, obj, info):
        logger.info('Retracting %s' % obj.uniqueId)
        if not info.published:
            logger.warning(
                "Retracting object %s which is not published." % obj.uniqueId)

        obj = self.recurse(self.before_retract, False, obj, obj)
        self.call_retract_script(obj)
        self.recurse(self.after_retract, False, obj, obj)

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
