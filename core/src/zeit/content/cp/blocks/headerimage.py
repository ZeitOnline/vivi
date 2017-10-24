from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


class HeaderImageBlock(zeit.content.cp.blocks.block.Block):

    grok.implements(zeit.content.cp.interfaces.IHeaderImageBlock)
    type = 'headerimage'

    image = zeit.cms.content.property.SingleResource('.image')
    animate = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'animate',
        zeit.content.cp.interfaces.IHeaderImageBlock['animate'])


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = HeaderImageBlock
    title = _('Header image block')
