# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import grokcore.component
import pytz
import zeit.cms.checkout.interfaces
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

    @property
    def has_semantic_change(self):
        return NotImplemented


hsc_field = zeit.cms.content.interfaces.ISemanticChange['has_semantic_change']


class SemanticChangeLocal(SemanticChange):

    grokcore.component.context(zeit.cms.checkout.interfaces.ILocalContent)

    ANNOTATION_KEY = 'zeit.cms.content.semanticchange.has_semantic_change'

    @property
    def has_semantic_change(self):
        ann = zope.annotation.interfaces.IAnnotations(self.context)
        return ann.get(self.ANNOTATION_KEY, hsc_field.default)

    @has_semantic_change.setter
    def has_semantic_change(self, value):
        ann = zope.annotation.interfaces.IAnnotations(self.context)
        ann[self.ANNOTATION_KEY] = value


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.interfaces.IObjectCreatedEvent)
def set_semantic_change_on_create(context, event):
    if zope.lifecycleevent.IObjectCopiedEvent.providedBy(event):
        return
    lsc = zope.security.proxy.removeSecurityProxy(
        zeit.cms.content.interfaces.ISemanticChange(context))
    lsc.last_semantic_change = datetime.datetime.now(pytz.UTC)
