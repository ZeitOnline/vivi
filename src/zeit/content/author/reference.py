# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore
import lxml.objectify
import zeit.cms.content.interfaces
import zeit.content.author.interfaces


@grokcore.component.adapter(
    zeit.content.author.interfaces.IAuthor, name='author')
@grokcore.component.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    node = lxml.objectify.E.author(href=context.uniqueId)
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(node)
    return node


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.content.author.interfaces.IAuthor

    def update_with_context(self, node, context):
        node.display_name = context.computed_display_name
