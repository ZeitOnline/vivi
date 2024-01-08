import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


@grok.implementer(zeit.content.cp.interfaces.IHeaderImageBlock)
class HeaderImageBlock(zeit.content.cp.blocks.block.Block):
    type = 'headerimage'

    image = zeit.cms.content.property.SingleResource('.image')
    animate = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'animate', zeit.content.cp.interfaces.IHeaderImageBlock['animate']
    )


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = HeaderImageBlock
    title = _('Header image block')
