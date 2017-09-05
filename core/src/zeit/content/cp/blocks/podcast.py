from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface


class PodcastBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IPodcastBlock)

    episode_id = zeit.cms.content.property.ObjectPathProperty(
        '.id', zeit.content.cp.interfaces.IPodcastBlock['episode_id'])


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'podcast', _('Podcast block'))
