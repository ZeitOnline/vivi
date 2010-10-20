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


class Image(zeit.edit.block.Element,
            grokcore.component.MultiAdapter):

    grokcore.component.adapts(
      zeit.content.article.edit.interfaces.IEditableBody,
      gocept.lxml.interfaces.IObjectified)
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IImage)
    grokcore.component.provides(
        zeit.content.article.edit.interfaces.IImage)

    type = 'image'
    grokcore.component.name(type)

    image = zeit.cms.content.property.SingleResource(
        '.', xml_reference_name='image', attributes=('src',))



class Factory(zeit.content.article.edit.block.BlockFactory):

    element_type = Image.type
    title = _('Image')
    grokcore.component.name(element_type)

    def get_xml(self):
        return lxml.objectify.E.image()
