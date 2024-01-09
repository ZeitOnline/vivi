import grokcore.component as grok

from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import IPodcast
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(IPodcast)
class Podcast(zeit.content.article.edit.block.Block):
    type = 'podcast'

    episode_id = ObjectPathAttributeProperty('.', 'id', IPodcast['episode_id'])
    provider = ObjectPathAttributeProperty('.', 'provider', IPodcast['provider'])


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = Podcast
    title = _('Podcast block')
