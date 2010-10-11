# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component
import zeit.content.article.interfaces
import zeit.edit.block
import zeit.edit.interfaces


class Paragraph(zeit.edit.block.Element,
                grokcore.component.MultiAdapter):

    grokcore.component.adapts(zeit.content.article.interfaces.IEditableBody,
                              gocept.lxml.interfaces.IObjectified)
    grokcore.component.name('p')
    grokcore.component.provides(zeit.edit.interfaces.IElement)
