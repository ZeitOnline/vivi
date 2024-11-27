import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IImageRow)
class ImageRow(zeit.content.article.edit.block.Block):
    type = 'image_row'
    display_mode = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'display_mode')
    variant_name = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'variant_name')
    images = zeit.cms.content.reference.ReferenceProperty('.image', 'image')


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = ImageRow
    title = _('Image Row')
