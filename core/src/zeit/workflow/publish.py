# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime
import pytz

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.workflow.interfaces

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
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(self.context))
        # TODO create remotetask to actually publish. The remotetask would send
        # an IPublishedEvent then. For now set published
        info.published = True
        info.date_last_published = datetime.datetime.now(pytz.UTC)

    def retract(self):
        """Retract object."""
        # TODO create remotetask to actually retract the object.
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        info.published = False
