import importlib.resources

import grokcore.component as grok
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.cms.type
import zeit.content.video.interfaces


@zope.interface.implementer(zeit.content.video.interfaces.IPlaylist, zeit.cms.interfaces.IAsset)
class Playlist(zeit.cms.content.metadata.CommonMetadata):
    default_template = (importlib.resources.files(__package__) / 'playlist-template.xml').read_text(
        'utf-8'
    )

    videos = zeit.cms.content.reference.MultiResource('.body.videos.video', 'related')

    id_prefix = 'pls'


class PlaylistType(zeit.cms.type.XMLContentTypeDeclaration):
    title = _('Playlist')
    interface = zeit.content.video.interfaces.IPlaylist
    addform = zeit.cms.type.SKIP_ADD
    factory = Playlist
    type = 'playlist'


@grok.adapter(zeit.content.video.interfaces.IPlaylist, name='playlist')
@grok.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def references(context):
    if context.videos:
        return context.videos
    return []
