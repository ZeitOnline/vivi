from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference
import zeit.content.audio.interfaces
import zeit.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IAudio)
class Audio(zeit.content.article.edit.block.Block):

    type = 'audio'
    # In the future we might switch this to use a Reference, so we can e.g.
    # express "this audio fully represents this article".
    references = zeit.content.article.edit.reference.SingleResource(
        '.', 'related')


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Audio
    title = _('Audio')


@grok.adapter(zeit.content.article.edit.interfaces.IArticleArea,
              zeit.content.audio.interfaces.IAudio,
              int)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_content(body, context, position):
    block = Factory(body)(position)
    block.references = context
    return block
