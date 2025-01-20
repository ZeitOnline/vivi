import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.content.image.interfaces


class IVideoRendition(zope.interface.interfaces.IInterface):
    url = zope.schema.URI(title=_('URI of the rendition'), required=False, readonly=True)

    frame_width = zope.schema.Int(title=_('Width of the Frame'))

    # milliseconds (we inherited this from Brightcove)
    video_duration = zope.schema.Int(title=_('Duration of the rendition'))


class VideoKindSource(zeit.cms.content.sources.SimpleFixedValueSource):
    values = ['livestream']


class IVideo(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.content.interfaces.IXMLContent,
    zeit.cms.content.interfaces.ISkipDefaultChannel,
):
    external_id = zope.schema.TextLine(title=_('External ID'), readonly=True)

    expires = zope.schema.Datetime(
        title=_('Video expires on'), required=False, readonly=True, default=None
    )

    renditions = zope.schema.Tuple(
        title=_('Renditions of the Video'),
        required=False,
        readonly=True,
        default=(),
        unique=False,
        value_type=zope.schema.Object(schema=IVideoRendition),
    )

    highest_rendition_url = zope.interface.Attribute(
        'URL of the rendition with the highest resolution'
    )

    video_still_copyright = zope.schema.TextLine(title=_('Video still copyright'), required=False)

    seo_slug = zope.interface.Attribute('URL tail for SEO.')

    has_advertisement = zope.schema.Bool(title=_('Has advertisement'), default=True)

    live_url_base = zope.schema.URI(title=_('URL'), required=False, readonly=True)

    kind = zope.schema.Choice(title=_('Video type'), source=VideoKindSource(), required=False)


class VideoSource(zeit.cms.content.contentsource.CMSContentSource):
    name = 'video'
    check_interfaces = (IVideo,)


videoSource = VideoSource()


class IPlayer(zope.interface.Interface):
    """Extension point to access media information, e.g. still image or
    video source URLs, since those may be volatile.
    """

    def get_video(id):
        """Returns a dict with at least the following keys:
        * renditions: list of IVideoRendition
        """
