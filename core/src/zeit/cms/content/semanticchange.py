# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import pytz
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.interface
import zope.lifecycleevent.interfaces
import zope.security.proxy


class SemanticChange(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.cms.content.interfaces.ISemanticChange)

    last_semantic_change = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ISemanticChange['last_semantic_change'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'last-semantic-change')


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.interfaces.IObjectCreatedEvent)
def set_semantic_change_on_create(context, event):
    if zope.lifecycleevent.IObjectCopiedEvent.providedBy(event):
        return
    lsc = zope.security.proxy.removeSecurityProxy(
        zeit.cms.content.interfaces.ISemanticChange(context))
    lsc.last_semantic_change = datetime.datetime.now(pytz.UTC)
