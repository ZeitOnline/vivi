import grokcore.component as grok

from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IImageParallaxProperties)
class ImageParallaxProperties(zeit.content.article.edit.block.Block):
    type = 'image_parallax_properties'

    show_caption = ObjectPathAttributeProperty(
        '.',
        'show_caption',
        zeit.content.article.edit.interfaces.IImageParallaxProperties['show_caption'],
    )
    show_source = ObjectPathAttributeProperty(
        '.',
        'show_source',
        zeit.content.article.edit.interfaces.IImageParallaxProperties['show_source'],
    )


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = ImageParallaxProperties
    title = _('Image Parallax Properties')
