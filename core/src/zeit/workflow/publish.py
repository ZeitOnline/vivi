# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime
import logging
import pytz

import zope.component
import zope.event
import zope.interface

import lovely.remotetask.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
from zeit.cms.i18n import MessageFactory as _


logger = logging.getLogger(__name__)


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
        self.tasks.add(u'zeit.workflow.publish', self.context.uniqueId)

    def retract(self):
        """Retract object."""
        # TODO create remotetask to actually retract the object.
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        info.published = False
        self.log(self.context, _('Retracted'))

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

    inputSchema = zope.schema.URI(
        title=u"Unique ID")

    def __call__(self, service, jobid, input):
        logger.info('Publishing %s' % input)
        obj = self.repository.getContent(input)
        info = zeit.cms.workflow.interfaces.IPublishInfo(obj)
        if not info.can_publish():
            return
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(obj))
        info.published = True
        info.date_last_published = datetime.datetime.now(pytz.UTC)

        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(obj, _('Published'))

        zope.event.notify(
            zeit.cms.workflow.interfaces.PublishedEvent(obj))

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
