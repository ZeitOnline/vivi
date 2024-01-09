import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.reference
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.interfaces


@grok.implementer(zeit.content.cp.interfaces.IPlaylistBlock)
class PlaylistBlock(zeit.content.cp.blocks.block.Block):
    type = 'playlist'

    referenced_playlist = zeit.cms.content.reference.SingleResource(
        '.block', xml_reference_name='related'
    )


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = PlaylistBlock
    title = _('Video Bar')


@grok.adapter(zeit.content.cp.interfaces.IPlaylistBlock)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def cms_content_iter(context):
    playlist = context.referenced_playlist
    if playlist is not None:
        yield playlist
