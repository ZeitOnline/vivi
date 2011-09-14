# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zope.interface
import zope.schema


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/brightcove'


class IAPIConnection(zope.interface.Interface):
    """Brightcove API connection."""


class IBrightcoveObject(zope.interface.Interface):
    """A representation of an object as stored in Brightcove."""


class SerieSource(zeit.cms.content.sources.SimpleXMLSource):
    config_url = 'source-serie'
    product_configuration = 'zeit.brightcove'


class IBrightcoveContent(zeit.cms.interfaces.ICMSContent):

    # XXX obsolete, remove when it's easy

    id = zope.schema.Int(
        title=_('Id'),
        readonly=True)

    id_prefix = zope.interface.Attribute(
        'Prefix for IDs used in XML references for assets (vid or pls)')

    title = zope.schema.TextLine(
        title=_("Title"))

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=True,
        max_length=170,
        missing_value='')

    thumbnail = zope.schema.URI(
        title=_('URI of the thumbnail'),
        required=False,
        readonly=True)

    brightcove_thumbnail = zope.schema.URI(
        title=_('URI of the thumbnail'),
        required=False,
        readonly=True)

    item_state = zope.schema.Choice(
        title=_("State"),
        required=True,
        readonly=True,
        values=("ACTIVE", "INACTIVE", "DELETED"))


class IVideo(IBrightcoveContent,
             zeit.cms.related.interfaces.IRelatedContent):
    """A video."""

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


class IPlaylist(IBrightcoveContent):
    """A playlist."""
    video_ids = zope.schema.Tuple(
        title=_("Video IDs"),
        required=False,
        default=(),
        unique=False,
        value_type=zope.schema.URI(
            title=_('URI of the Playlist-Video'),
            required=False,
            readonly=True)
    )


class BrightcoveSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'brightcove-content'
    check_interfaces = (IVideo, IPlaylist)


brightcoveSource = BrightcoveSource()


class VideoSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'brightcove-videos'
    check_interfaces = (IVideo,)


videoSource = VideoSource()


class IVideoAsset(zope.interface.Interface):

    audio_id = zope.schema.TextLine(
        title=_('Audio id'),
        required=False)

    video = zope.schema.Choice(
        title=_('Video'),
        required=False,
        source=brightcoveSource)

    video_2 = zope.schema.Choice(
        title=_('Video 2'),
        required=False,
        source=brightcoveSource)
