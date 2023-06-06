from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IAnimation)
class Animation(zeit.content.article.edit.block.Block):

    type = 'animation'
    animation = zeit.cms.content.reference.SingleResource(".", "related")


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Animation
    title = _('Animation')
