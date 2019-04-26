from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


class PodcastBlock(zeit.content.cp.blocks.block.Block):

    grok.implements(zeit.content.cp.interfaces.IPodcastBlock)
    type = 'podcast'

    episode_id = zeit.cms.content.property.ObjectPathProperty(
        '.id', zeit.content.cp.interfaces.IPodcastBlock['episode_id'])


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = PodcastBlock
    title = _('Podcast block')
