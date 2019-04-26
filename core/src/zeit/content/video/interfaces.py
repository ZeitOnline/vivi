from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zope.schema


class IVideoContent(zeit.cms.content.interfaces.ICommonMetadata,
                    zeit.cms.content.interfaces.IXMLContent,
                    zeit.cms.content.interfaces.ISkipDefaultChannel):
    """Video like content.

    This could be a video or a playlist.

    """

    thumbnail = zope.schema.URI(
        title=_('URI of the thumbnail'),
        required=False,
        readonly=True)

    id_prefix = zope.schema.TextLine(
        title=_('Id prefix'),
        required=True,
        readonly=True)


class IVideoRendition(zope.interface.interfaces.IInterface):
    url = zope.schema.URI(
        title=_('URI of the rendition'),
        required=False,
        readonly=True)

    frame_width = zope.schema.Int(
        title=_('Width of the Frame'))

    video_duration = zope.schema.Int(
        title=_('Duration of the rendition'))


class IVideo(IVideoContent):

    external_id = zope.schema.TextLine(
        title=_('External ID'),
        readonly=True)

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

    renditions = zope.schema.Tuple(
        title=_("Renditions of the Video"),
        required=False,
        readonly=True,
        default=(),
        unique=False,
        value_type=zope.schema.Object(
            schema=IVideoRendition
        )
    )

    highest_rendition_url = zope.interface.Attribute(
        'URL of the rendition with the highest resolution')

    video_still_copyright = zope.schema.TextLine(
        title=_('Video still copyright'),
        required=False)

    seo_slug = zope.interface.Attribute('URL tail for SEO.')

    has_advertisement = zope.schema.Bool(
        title=_('Has advertisement'),
        default=True)


class VideoSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'video'
    check_interfaces = (IVideo,)


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


class PlaylistSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'playlist'
    check_interfaces = (IPlaylist,)


class VideoOrPlaylistSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'video-or-playlist'
    check_interfaces = IVideo, IPlaylist


videoOrPlaylistSource = VideoOrPlaylistSource()


class IPlayer(zope.interface.Interface):
    """Extension point to access media information, e.g. still image or
    video source URLs, since those may be volatile.
    """

    def get_video(id):
        """Must return a dict with at least the following keys:
        * thumbnail: str
        * video_still: str
        * renditions: list of IVideoRendition
        """
