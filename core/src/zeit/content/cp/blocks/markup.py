from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


@grok.implementer(zeit.content.cp.interfaces.IMarkupBlock)
class MarkupBlock(zeit.content.cp.blocks.block.Block):

    type = 'markup'

    text = zeit.cms.content.property.Structure('.text')
    alignment = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'align', zeit.content.cp.interfaces.IMarkupBlock['alignment'])


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = MarkupBlock
    title = _('Markup block')
