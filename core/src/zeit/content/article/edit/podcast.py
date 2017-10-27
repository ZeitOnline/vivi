from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import IPodcast
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


class Podcast(zeit.content.article.edit.block.Block):

    grok.implements(IPodcast)
    type = 'podcast'

    episode_id = ObjectPathAttributeProperty(
        '.', 'id', IPodcast['episode_id'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Podcast
    title = _('Podcast block')
