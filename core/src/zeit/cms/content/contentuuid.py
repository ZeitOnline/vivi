# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import uuid
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.connector.interfaces
import zeit.cms.content.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.interface


class ContentUUID(object):

    zope.interface.implements(zeit.cms.content.interfaces.IUUID)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.IUUID,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('id', ),)

    def __init__(self, context):
        self.context = context


@zope.component.adapter(ContentUUID)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)

@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def set_uuid(context, event):
    content_uuid = zeit.cms.content.interfaces.IUUID(context)
    if content_uuid.id is not None:
        return
    content_uuid.id = uuid.uuid4()
