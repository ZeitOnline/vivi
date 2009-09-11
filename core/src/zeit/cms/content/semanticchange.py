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
