import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference


@grok.implementer(zeit.content.article.edit.interfaces.IScrollyImage)
class ScrollyImage(zeit.content.article.edit.reference.Reference):
    type = 'scrolly_image'

    text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'text', zeit.content.article.edit.interfaces.IScrollyImage['text']
    )
    text_display = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'text-display',
        zeit.content.article.edit.interfaces.IScrollyImage['text_display'],
        use_default=True,
    )
    layout_desktop = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'layout-desktop',
        zeit.content.article.edit.interfaces.IScrollyImage['layout_desktop'],
        use_default=True,
    )
    layout_mobile = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'layout-mobile',
        zeit.content.article.edit.interfaces.IScrollyImage['layout_mobile'],
        use_default=True,
    )


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = ScrollyImage
    title = _('Scrollytelling Image')
