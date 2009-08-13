# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.dublincore.interfaces
import zope.interface
import zope.security.proxy


class Modified(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.cms.workflow.interfaces.IModified)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.workflow.interfaces.IModified,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('last_modified_by', ))

    @property
    def date_last_modified(self):
        return zope.dublincore.interfaces.IDCTimes(self.context).modified


@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_last_modified_by(context, event):
    modified = zeit.cms.workflow.interfaces.IModified(context, None)
    if modified is None:
        return
    zope.security.proxy.removeSecurityProxy(modified).last_modified_by = (
        event.principal.id)


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.cms.workflow.interfaces.IModified

    def update_with_context(self, entry, modified):
        date = ''
        if modified.date_last_modified:
            date = modified.date_last_modified.isoformat()
        entry.set('date-last-modified', date)
