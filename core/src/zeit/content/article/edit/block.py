# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import lxml.objectify
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces


class BlockFactory(zeit.edit.block.ElementFactory):

    grokcore.component.baseclass()
    grokcore.component.context(
        zeit.content.article.edit.interfaces.IEditableBody)

    def get_xml(self):
        return getattr(lxml.objectify.E, self.element_type)()
