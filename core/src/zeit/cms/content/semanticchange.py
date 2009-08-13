# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.interface


class SemanticChange(zeit.cms.content.dav.DAVPropertiesAdapter):

    zope.interface.implements(zeit.cms.content.interfaces.ISemanticChange)

    last_semantic_change = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ISemanticChange['last_semantic_change'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'last-semantic-change')


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.cms.content.interfaces.ISemanticChange

    def update_with_context(self, entry, lsc):
        date = ''
        if lsc.last_semantic_change:
            date = lsc.last_semantic_change.isoformat()
        entry.set('last-semantic-change', date)
