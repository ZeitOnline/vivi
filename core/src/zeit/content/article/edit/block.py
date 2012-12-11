# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import lxml.objectify
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.edit.block
import zeit.edit.interfaces


@grokcore.component.adapter(zeit.edit.interfaces.IElement)
@grokcore.component.implementer(zeit.content.article.interfaces.IArticle)
def article_for_element(context):
    return zeit.content.article.interfaces.IArticle(context.__parent__, None)


class BlockFactory(zeit.edit.block.ElementFactory):

    grokcore.component.baseclass()
    grokcore.component.context(
        zeit.content.article.edit.interfaces.IEditableBody)
    # No title so we are excluded from @@block-factories -- our blocks are
    # created via the toolbar, and should not appear in the module library.
    title = None

    def get_xml(self):
        return getattr(lxml.objectify.E, self.element_type)()
