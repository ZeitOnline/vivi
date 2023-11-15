from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.rawtext


@grok.implementer(zeit.content.cp.interfaces.IRawTextBlock)
class RawTextBlock(zeit.content.modules.rawtext.RawText, zeit.content.cp.blocks.block.Block):
    type = 'rawtext'


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = RawTextBlock
    title = _('raw text block')


@grok.adapter(zeit.content.cp.interfaces.IArea, zeit.content.text.interfaces.IText, int)
@grok.implementer(zeit.edit.interfaces.IElement)
def make_block_from_content(container, content, position):
    block = Factory(container)(position)
    block.text_reference = content
    return block
