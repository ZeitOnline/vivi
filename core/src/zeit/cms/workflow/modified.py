# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.dublincore.interfaces
import zope.interface


class Modified(object):

    zope.interface.implements(zeit.cms.workflow.interfaces.IModified)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IModified,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('last_modified_by', ))

    def __init__(self, context):
        self.context = context

    @property
    def date_last_modified(self):
        return zope.dublincore.interfaces.IDCTimes(self.context).modified


@zope.component.adapter(Modified)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def modifiedProperties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_last_modified_by(context, event):
    modified = zeit.cms.workflow.interfaces.IModified(context, None)
    if modified is None:
        return
    modified.last_modified_by = event.principal.id


