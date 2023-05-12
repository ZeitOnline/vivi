from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.animation.animation
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IAnimatedHeader)
class AnimatedHeader(zeit.content.article.edit.block.Block):

    type = 'animatedheader'
    animation = zeit.cms.content.reference.SingleResource(".", "related")


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = AnimatedHeader
    title = _('Animated header')
