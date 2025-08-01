import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
from zeit.content.cp.interfaces import IPodcastHeaderBlock, IPodcastMetadataBlock
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


@grok.implementer(IPodcastHeaderBlock)
class PodcastHeaderBlock(zeit.content.cp.blocks.block.Block):
    type = 'podcastheader'


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = PodcastHeaderBlock
    title = _('Podcastblock')


@grok.implementer(IPodcastMetadataBlock)
class PodcastMetadataBlock(zeit.content.cp.blocks.block.Block):
    type = 'podcastmetadata'

    description = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'description', zeit.content.cp.interfaces.IPodcastMetadataBlock['description']
    )


class PodcastMetadataFactory(zeit.content.cp.blocks.block.BlockFactory):
    produces = PodcastMetadataBlock
    title = _('Podcast Metadata')
