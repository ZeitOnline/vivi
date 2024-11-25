import grokcore.component as grok
import lxml
import zope

from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.source import LEGACY_DISPLAY_MODE_SOURCE, LEGACY_VARIANT_NAME_SOURCE
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IImageRow)
class ImageRow(zeit.content.article.edit.block.Block):
    type = 'image_row'
    _display_mode = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'display_mode')
    _variant_name = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'variant_name')
    _images = []

    @property
    def images(self):
        result = []
        for element in self.xml.getchildren():
            reference = zope.component.queryMultiAdapter(
                (self, element),
                zeit.cms.content.interfaces.IReference,
                name='image',
            )
            caption = element.get('caption', None)
            alt_text = element.get('alt_text', None)
            result.append((reference.target, caption, alt_text))
        return result

    @images.setter
    def images(self, value):
        # remove all children of parent xml
        for child in self.xml.getchildren():
            self.xml.remove(child)
        # go through value and add children
        for item in value:
            image = item[0]
            caption = item[1]
            alt_text = item[2]
            # only add if image exists. otherwise ignore.
            if image is not None:
                element = lxml.etree.Element(
                    'image',
                )
                element.set('base-id', image.uniqueId)
                element.set('type', image.master_image.split('.')[1])
                if caption is not None:
                    element.set('caption', caption)
                if alt_text is not None:
                    element.set('alt_text', alt_text)
                self.xml.append(element)
        self._images = value

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
        max_images_dict = {'float': 1, 'column-width': 2, 'large': 3}
        max_images = max_images_dict.get(value, 1)
        # Remove images in xml if there are too many
        for i in range(len(self.xml.getchildren()) - max_images):
            self.xml.remove(self.xml.getchildren()[-1])
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


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = ImageRow
    title = _('Image Row')