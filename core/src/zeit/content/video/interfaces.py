# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.tagging.whitelist
import zope.schema


class IVideoContent(zeit.cms.content.interfaces.ICommonMetadata,
                    zeit.cms.content.interfaces.IXMLContent):
    """Video like content.

    This could be a video or a playlist.

    """

    thumbnail = zope.schema.URI(
        title=_('URI of the thumbnail'),
        required=False,
        readonly=True)


class IVideo(IVideoContent):

    has_recensions = zope.schema.Bool(
        title=_('Has recension content'),
        default=False)

    expires = zope.schema.Datetime(
        title=_('Video expires on'),
        required=False,
        readonly=True,
        default=None)

    video_still = zope.schema.URI(
        title=_('URI of the still image'),
        required=False,
        readonly=True)

    flv_url = zope.schema.URI(
        title=_('URI of the video file'),
        required=False,
        readonly=True)

    keywords = zope.schema.Tuple(
        title=_("Keywords"),
        required=False,
        default=None,
        value_type=zope.schema.Choice(
            source=zeit.cms.tagging.whitelist.WhitelistSource()))


class VideoSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'video'
    check_interfaces = IVideo


class IPlaylist(IVideoContent):

    videos = zope.schema.Tuple(
        title=_("Video IDs"),
        required=False,
        readonly=True,
        default=(),
        unique=False,
        value_type=zope.schema.Choice(
            title=_('Videos in the playlist'),
            source=VideoSource()))


class VideoOrPlaylistSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'video-or-playlist'
    check_interfaces = IVideo, IPlaylist


videoOrPlaylistSource = VideoOrPlaylistSource()


class IVideoAsset(zope.interface.Interface):

    audio_id = zope.schema.TextLine(
        title=_('Audio id'),
        required=False)

    video = zope.schema.Choice(
        title=_('Video'),
        required=False,
        source=videoOrPlaylistSource)

    video_2 = zope.schema.Choice(
        title=_('Video 2'),
        required=False,
        source=videoOrPlaylistSource)
