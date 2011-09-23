# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.content.video.interfaces
import zope.interface


class Playlist(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(zeit.content.video.interfaces.IPlaylist,
                              zeit.cms.interfaces.IAsset)

    default_template = '<playlist></playlist>'

    zeit.cms.content.dav.mapProperties(
        zeit.content.video.interfaces.IPlaylist,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('video_ids', 'thumbnail'))

    id_prefix = 'pls'

class PlaylistType(zeit.cms.type.XMLContentTypeDeclaration):

    title = _('Playlist')
    interface = zeit.content.video.interfaces.IPlaylist
    addform = zeit.cms.type.SKIP_ADD
    factory = Playlist
    type = 'playlist'
