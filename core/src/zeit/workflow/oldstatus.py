# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.workflow.interfaces


class OldStatus(object):
    """Support old status."""

    zope.interface.implements(zeit.workflow.interfaces.IOldCMSStatus)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IOldCMSStatus,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('status', ),
        live=True)

    def __init__(self, context):
        self.context = context


@zope.component.adapter(OldStatus)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)

@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.workflow.interfaces.IBeforePublishEvent)
def set_status(context, event):
    old_status = zeit.workflow.interfaces.IOldCMSStatus(context)
    if old_status.status != 'OK':
        old_status.status = 'OK'

@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.workflow.interfaces.IRetractedEvent)
def remove_status(context, event):
    old_status = zeit.workflow.interfaces.IOldCMSStatus(context)
    if old_status.status is not None:
        old_status.status = None
