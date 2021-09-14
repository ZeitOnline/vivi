from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


@grok.implementer(zeit.content.cp.interfaces.IPodcastBlock)
class PodcastBlock(zeit.content.cp.blocks.block.Block):

    type = 'podcast'

    episode_id = zeit.cms.content.property.ObjectPathProperty(
        '.id', zeit.content.cp.interfaces.IPodcastBlock['episode_id'])
    provider = zeit.cms.content.property.ObjectPathProperty(
        '.provider', zeit.content.cp.interfaces.IPodcastBlock['provider'])


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = PodcastBlock
    title = _('Podcast block')
