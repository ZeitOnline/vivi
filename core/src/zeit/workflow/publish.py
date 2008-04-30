# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime
import logging
import pytz

import zope.component
import zope.event
import zope.interface
import zope.security.management

import zope.app.security.interfaces

import lovely.remotetask.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
from zeit.cms.i18n import MessageFactory as _


logger = logging.getLogger(__name__)


def login(principal):
    interaction = zope.security.management.getInteraction()
    participation = interaction.participations[0]
    auth = zope.component.getUtility(
        zope.app.security.interfaces.IAuthentication)
    participation.setPrincipal(auth.getPrincipal(principal))


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
        self.log(self.context, _('Retracting scheduled.'))
        self.tasks.add(u'zeit.workflow.retract',
                       TaskDescription(self.context.uniqueId))

    @property
    def tasks(self):
        return zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')

    def log(self, obj, msg):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, msg)



class PublishTask(object):
    """Publish object."""

    zope.interface.implements(lovely.remotetask.interfaces.ITask)

    #inputSchema = zope.schema.Object()  # XXX

    def __call__(self, service, jobid, input):
        logger.info('Publishing %s' % input)
        login(input.principal)
        obj = self.repository.getContent(input.uniqueId)
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        if not info.can_publish():
            return
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(obj))

        info.published = True
        info.date_last_published = datetime.datetime.now(pytz.UTC)

        # XXX actually publish

        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, _('Published'))

        zope.event.notify(
            zeit.cms.workflow.interfaces.PublishedEvent(obj))

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class RetractTask(object):
    """Retract an object."""

    zope.interface.implements(lovely.remotetask.interfaces.ITask)

    #inputSchema = zope.schema.Object()  # XXX

    def __call__(self, service, jobid, input):
        logger.info('Retracting %s' % input)
        login(input.principal)
        obj = self.repository.getContent(input.uniqueId)
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        if not info.published:
            logger.warning(
                "Tried to retract an object which is not published.")
            return
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforeRetractEvent(obj))

        # XXX retract

        info.published = False
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, _('Retracted'))
        zope.event.notify(
            zeit.cms.workflow.interfaces.RetractedEvent(obj))

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
