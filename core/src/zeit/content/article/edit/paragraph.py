# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component
import lxml.etree
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces


class Paragraph(zeit.edit.block.Element,
                grokcore.component.MultiAdapter):

    grokcore.component.adapts(
      zeit.content.article.edit.interfaces.IEditableBody,
      gocept.lxml.interfaces.IObjectified)
    grokcore.component.name('p')
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IParagraph)
    grokcore.component.provides(
        zeit.content.article.edit.interfaces.IParagraph)

    type = 'paragraph'

    @property
    def text(self):
        return lxml.etree.tostring(self.xml)
