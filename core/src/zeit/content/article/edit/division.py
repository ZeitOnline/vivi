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


class Division(zeit.edit.block.Element,
                grokcore.component.MultiAdapter):

    grokcore.component.adapts(
      zeit.content.article.edit.interfaces.IEditableBody,
      gocept.lxml.interfaces.IObjectified)
    grokcore.component.name('division')
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IDivision)
    grokcore.component.provides(
        zeit.content.article.edit.interfaces.IDivision)

    type = 'division'

    teaser = zeit.cms.content.property.ObjectPathAttributeProperty(
      '.', 'teaser', zeit.content.article.edit.interfaces.IDivision['teaser'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    element_type = Division.type
    title = _('Division')
    grokcore.component.name(element_type)

    def get_xml(self):
        return lxml.objectify.E.division(type='page')
