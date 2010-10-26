# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.lxml.interfaces
import grokcore.component
import lxml.objectify
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component


class Image(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IImage)
    type = 'image'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout', zeit.content.article.edit.interfaces.IImage['layout'])

    @property
    def image(self):
        unique_id = self.xml.get('src')
        return zeit.cms.interfaces.ICMSContent(unique_id, None)

    @image.setter
    def image(self, value):
        node = zope.component.getAdapter(
            value, zeit.cms.content.interfaces.IXMLReference,
            name='image')
        # We have to save a few attributes before we replace the whole node
        name = self.__name__
        layout = self.layout
        self.xml.getparent().replace(self.xml, node)
        self.xml = node
        # Restore saved attributes
        self.__name__ = name
        self.layout =  layout
        self._p_changed = True


class Factory(zeit.content.article.edit.block.BlockFactory):

    element_type = Image.type
    title = _('Image')
    grokcore.component.name(element_type)

    def get_xml(self):
        return lxml.objectify.E.image()


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IEditableBody,
                            zeit.content.image.interfaces.IImage)
@grokcore.component.implementer(zeit.edit.interfaces.IElement)
def factor_image_block_from_image(body, image):
    block = Factory(body)()
    block.image = image
    return block
