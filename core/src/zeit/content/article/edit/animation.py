from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.animation.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference
import zeit.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IAnimation)
class Animation(zeit.content.article.edit.block.Block):

    type = 'animation'
    animation = zeit.content.article.edit.reference.SingleResource(
        '.', 'related')


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Animation
    title = _('Animation')


@grok.adapter(zeit.content.article.edit.interfaces.IArticleArea,
              zeit.content.animation.interfaces.IAnimation,
              int)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_content(body, context, position):
    block = Factory(body)(position)
    block.animation = context
    return block
