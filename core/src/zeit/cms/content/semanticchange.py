# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.component
import zope.interface


class SemanticChange(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.cms.content.interfaces.ISemanticChange)

    last_semantic_change = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ISemanticChange['last_semantic_change'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'last-semantic-change')

    def __init__(self, context):
        self.context = context


@zope.component.adapter(zeit.cms.content.interfaces.ISemanticChange)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
