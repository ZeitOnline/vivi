from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.interfaces
import zeit.edit.block
import zope.interface


class PlaylistBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IPlaylistBlock)

    referenced_playlist = zeit.cms.content.property.SingleResource(
        '.block', xml_reference_name='related', attributes=('href',))


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'playlist', _('Video Bar'))


@grok.adapter(zeit.content.cp.interfaces.IPlaylistBlock)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def cms_content_iter(context):
    playlist = context.referenced_playlist
    if playlist is not None:
        yield playlist
