import grokcore.component as grok
import lxml

from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.source import LEGACY_DISPLAY_MODE_SOURCE, LEGACY_VARIANT_NAME_SOURCE
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IImageRow)
class ImageRow(zeit.content.article.edit.block.Block):
    def __init__(self, context, xml):
        # call base constructor
        super(ImageRow, self).__init__(context, xml)
        # set xml object to default template, if it has no body
        if not self.xml.xpath('//body'):
            self.xml.append(lxml.etree.Element('body'))

    type = 'image_row'

    show_caption = ObjectPathAttributeProperty(
        '.', 'show_caption', zeit.content.article.edit.interfaces.IImageRow['show_caption']
    )
    show_source = ObjectPathAttributeProperty(
        '.', 'show_source', zeit.content.article.edit.interfaces.IImageRow['show_source']
    )
    _display_mode = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'display_mode')
    _variant_name = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'variant_name')
    images = zeit.cms.content.reference.MultiResource('.body.image', 'image')

    @property
    def display_mode(self):
        if self._display_mode is not None:
            return self._display_mode
        # backward compatibility by mapping old layout to display_mode
        layout = self.xml.get('layout', None)
        mapping = dict(list(LEGACY_DISPLAY_MODE_SOURCE(self)))
        return mapping.get(
            layout, zeit.content.article.edit.interfaces.IImage['display_mode'].default
        )

    @display_mode.setter
    def display_mode(self, value):
        self._display_mode = value

    @property
    def variant_name(self):
        if self._variant_name is not None:
            return self._variant_name
        # backward compatibility by mapping old layout to display_mode
        layout = self.xml.get('layout', None)
        mapping = dict(list(LEGACY_VARIANT_NAME_SOURCE(self)))
        return mapping.get(
            layout, zeit.content.article.edit.interfaces.IImage['variant_name'].default
        )

    @variant_name.setter
    def variant_name(self, value):
        self._variant_name = value

    # first_image = zeit.cms.content.reference.SingleResource('.image[1]', 'image')
    # second_image = zeit.cms.content.reference.SingleResource('.image[2]', 'image')
    # third_image = zeit.cms.content.reference.SingleResource('.image[3]', 'image')
    # first_image = zeit.cms.content.reference.SingleResource('.image-1', 'image')
    # second_image = zeit.cms.content.reference.SingleResource('.image-2', 'image')
    # third_image = zeit.cms.content.reference.SingleResource('.image-3', 'image')


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = ImageRow
    title = _('Image Row')
