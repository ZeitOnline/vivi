from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.embed


@grok.implementer(zeit.content.article.edit.interfaces.IEmbed)
class Embed(zeit.content.modules.embed.Embed, zeit.content.article.edit.block.Block):
    type = 'embed'


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = Embed
    title = _('Embed block')
