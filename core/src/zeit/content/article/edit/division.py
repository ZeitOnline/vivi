# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.lxml.interfaces
import grokcore.component
import lxml.objectify
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces


class Division(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    type = 'division'
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IDivision)

    teaser = zeit.cms.content.property.ObjectPathAttributeProperty(
      '.', 'teaser', zeit.content.article.edit.interfaces.IDivision['teaser'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Division
    title = _('Division')

    def get_xml(self):
        return lxml.objectify.E.division(type='page')
