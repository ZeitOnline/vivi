# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import lxml.objectify
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class RawXML(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IRawXML)
    type = 'raw'


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = RawXML
    title = _('Raw XML')

    def get_xml(self):
        return getattr(lxml.objectify.E, self.element_type)('\n\n')
