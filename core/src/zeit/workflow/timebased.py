# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import rwproperty

import zope.component
import zope.event
import zope.interface
import zope.location.location

import zeit.connector.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.workflow.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.workflow.interfaces

WORKFLOW_NS = zeit.workflow.interfaces.WORKFLOW_NS


class TimeBasedWorkflow(object):
    """Timebased workflow."""

    zope.interface.implements(zeit.workflow.interfaces.ITimeBasedPublishing)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IPublishInfo,
        WORKFLOW_NS, ('published', 'date_last_published'),
        live=True)
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing[
            'release_period'].fields[0],
        WORKFLOW_NS, 'released_from', live=True)
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing[
            'release_period'].fields[1],
        WORKFLOW_NS, 'released_to', live=True)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IPublishInfo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, ('date_first_released',),
        live=True)

    def __init__(self, context):
        self.context = context

    @rwproperty.getproperty
    def release_period(self):
        return self.released_from, self.released_to

    @rwproperty.setproperty
    def release_period(self, value):
        if value is None:
            value = None, None
        self.released_from, self.released_to = value


@zope.component.adapter(TimeBasedWorkflow)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def workflowProperties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


