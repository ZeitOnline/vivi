from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.rawtext


class RawTextBlock(
        zeit.content.modules.rawtext.RawText,
        zeit.content.cp.blocks.block.Block):

    grok.implements(zeit.content.cp.interfaces.IRawTextBlock)
    type = 'rawtext'


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = RawTextBlock
    title = _('raw text block')
