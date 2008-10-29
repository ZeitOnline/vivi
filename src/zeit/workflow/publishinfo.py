# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.workflow.interfaces


class NotPublishablePublishInfo(object):
    """A publish info which indicates that the content is not publishable."""

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.workflow.interfaces.IPublishInfo)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IPublishInfo,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('published', 'date_last_published'),
        live=True)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IPublishInfo,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, ('date_first_released',),
        live=True)

    def __init__(self, context):
        self.context = context

    def can_publish(self):
        return False


@zope.component.adapter(NotPublishablePublishInfo)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def workflowProperties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)
