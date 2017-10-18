from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.rawtext
import zeit.edit.block


class RawText(zeit.content.modules.rawtext.RawText,
              zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.implements(zeit.content.article.edit.interfaces.IRawText)
    type = 'rawtext'


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = RawText
    title = _('Raw text block')


@grok.adapter(zeit.content.article.edit.interfaces.IArticleArea,
              zeit.content.text.interfaces.IText,
              int)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_text(body, context, position):
    block = Factory(body)(position)
    block.text_reference = context
    return block
