# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Publish and retract actions."""

import datetime
import logging
import os.path
import subprocess
import pytz

import zope.component
import zope.event
import zope.interface
import zope.security.management

import zope.app.security.interfaces
import zope.app.appsetup.product

import lovely.remotetask.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
from zeit.cms.i18n import MessageFactory as _


logger = logging.getLogger(__name__)


class TaskDescription(object):
    """Data to be passed to publish/retract tasks."""

    def __init__(self, uniqueId):
        self.uniqueId = uniqueId
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
        self.tasks.add(u'zeit.workflow.publish',
                       TaskDescription(self.context.uniqueId))

    def retract(self):
        """Retract object."""
        self.log(self.context, _('Retracting scheduled'))
        self.tasks.add(u'zeit.workflow.retract',
                       TaskDescription(self.context.uniqueId))

    @property
    def tasks(self):
        return zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')

    def log(self, obj, msg):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, msg)



class PublishRetractTask(object):

    zope.interface.implements(lovely.remotetask.interfaces.ITask)
    #inputSchema = zope.schema.Object()  # XXX

    def __call__(self, service, jobid, input):
        uniqueId = input.uniqueId
        principal = input.principal
        self.login(principal)

        obj = self.repository.getContent(input.uniqueId)
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)

        self.run(obj, info)

    def cycle(self, obj):
        """checkout/checkin obj to sync data as necessary.

        The basic idea is that there are some event handlers which sync
        properties to xml on checkout/checkin.

        """
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(obj)
        if not manager.canCheckout:
            logger.error("Could not checkout %s" % obj.uniqueId)
            return obj
        checked_out = manager.checkout()

        manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
        if not manager.canCheckin:
            logger.error("Could not checkin %s" % obj.uniqeId)
            del checked_out.__parent__[checked_out.__name__]
            return obj
        return manager.checkin()

    def recurse(self, method, obj, *args):
        """Apply method recursively on obj."""
        stack = [obj]
        result_obj = None
        while stack:
            current_obj = stack.pop(0)
            logger.debug('%s %s' % (method, current_obj.uniqueId))
            new_obj = method(current_obj, *args)
            if zeit.cms.repository.interfaces.ICollection.providedBy(new_obj):
                stack.extend(new_obj.values())
            if result_obj is None:
                result_obj = new_obj

        return result_obj

    @staticmethod
    def login(principal):
        interaction = zope.security.management.getInteraction()
        participation = interaction.participations[0]
        auth = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication)
        participation.setPrincipal(auth.getPrincipal(principal))

    @property
    def log(self):
        return zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class PublishTask(PublishRetractTask):
    """Publish object."""

    def run(self, obj, info):
        logger.info('Publishing %s' % obj.uniqueId)
        if not info.can_publish():
            logger.error("Could not publish %s" % obj.uniqueId)
            self.log.log(
                obj, _("Could not publish because conditions not satisifed."))
            return

        obj = self.recurse(self.before_publish, obj)
        self.call_publish_script(obj)
        self.recurse(self.after_publish, obj)

    def before_publish(self, obj):
        """Do everything necessary before the actual publish."""

        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(obj))

        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = True
        # ARGH. This is evil. We need to put the publish time a few seconds
        # into the future to be *after* the cycle call below. During the cycle
        # the object will be most likely changed. It therefore would have a
        # modification after the publication and would be shown as stale in the
        # CMS.
        now = datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=60)
        info.date_last_published = now
        if not info.date_first_released:
            info.date_first_released = now

        new_obj = self.cycle(obj)
        return new_obj

    def call_publish_script(self, obj):
        """Actually do the publication."""
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        publish_script = config['publish-script']
        path_prefix = config['path-prefix']

        unique_ids = []
        self.recurse(self.get_unique_id, obj, unique_ids)

        # The publish script doesn't want URLs but local paths. Munge them.
        unique_ids = [
            os.path.join(
                path_prefix,
                uid.replace(zeit.cms.interfaces.ID_NAMESPACE, '', 1))
            for uid in unique_ids]

        # Call the script. This does the actual publish.
        proc = subprocess.Popen(
            [publish_script], bufsize=-1,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate('\n'.join(unique_ids))
        if stdout:
            logger.info("Publish script output:\n%s" % stdout)
        if stderr:
            logger.error("Publish script error:\n%s" % stderr)

    def after_publish(self, obj):
        self.log.log(obj, _('Published'))
        zope.event.notify(zeit.cms.workflow.interfaces.PublishedEvent(obj))
        return obj

    def get_unique_id(self, obj, unique_ids):
        unique_ids.append(obj.uniqueId)
        return obj


class RetractTask(PublishRetractTask):
    """Retract an object."""

    def run(self, obj, info):
        logger.info('Retracting %s' % obj.uniqueId)
        if not info.published:
            logger.warning(
                "Retracting object %s which is not published." % obj.uniqueId)


        obj = self.recurse(self.before_retract, obj)
        # XXX actually retract
        self.recurse(self.after_retract, obj)

    def before_retract(self, obj):
        """Do things before the actual retract."""
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforeRetractEvent(obj))
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        info.published = False
        self.log.log(obj, _('Retracted'))
        new_obj = self.cycle(obj)
        return new_obj

    def after_retract(self, obj):
        """Do things after retract."""
        zope.event.notify(zeit.cms.workflow.interfaces.RetractedEvent(obj))
        return obj

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
