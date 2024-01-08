import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.rawtext


@grok.implementer(zeit.content.article.edit.interfaces.IRawText)
class RawText(zeit.content.modules.rawtext.RawText, zeit.content.article.edit.block.Block):
    type = 'rawtext'


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = RawText
    title = _('Raw text block')


@grok.adapter(
    zeit.content.article.edit.interfaces.IArticleArea, zeit.content.text.interfaces.IText, int
)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_text(body, context, position):
    block = Factory(body)(position)
    block.text_reference = context
    return block
