# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zope.container.interfaces
import zope.interface
import zope.schema


class IAPIConnection(zope.interface.Interface):
    """Brightcove API connection."""


class IRepository(zope.container.interfaces.IItemContainer):
    """A repostory for accessing brightcove videos.


    Content from brightcove has unique ids in the form::

        brighcove:<type>:<id>.

    """


class SerieSource(zeit.cms.content.sources.SimpleXMLSource):
    config_url = 'source-serie'
    product_configuration = 'zeit.brightcove'


class IBCContent(zeit.cms.interfaces.ICMSContent):
     """Plain BrightCove-Content w/ just an uniqueId
     """


class IBrightcoveContent(IBCContent):

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

    supertitle = zope.schema.TextLine(
        title=_("Kicker"),
        description=_("Please take care of capitalisation."),
        max_length=1024,
        required=False,
        missing_value='')

    subtitle = zope.schema.Text(
        title=_("Video subtitle"),
        required=False,
        max_length=5000)

    ressort = zope.schema.Choice(
        title=_("Ressort"),
        source=zeit.cms.content.sources.NavigationSource())

    serie = zope.schema.Choice(
        title=_("Serie"),
        source= SerieSource(),
        required=False,
        missing_value='')

    product_id = zope.schema.Choice(
        title=_('Product id'),
        default='ZEDE',
        source=zeit.cms.content.sources.ProductSource())

    keywords = zope.schema.Tuple(
        title=_("Keywords"),
        required=False,
        default=(),
        unique=True,
        value_type=zope.schema.Object(
            zeit.cms.content.interfaces.IKeyword))

    dailyNewsletter = zope.schema.Bool(
        title=_("Daily newsletter"),
        description=_(
            "Should this article be listed in the daily newsletter?"),
        default=False)
    
    allow_comments = zope.schema.Bool(
        title=_("comments allowed"),
        description=_(
            "Are comments allowed for this video?"),
        default=False)

    banner = zope.schema.Bool(
        title=_("Banner"),
        default=False)

    banner_id = zope.schema.TextLine(
        title=_('Banner id'),
        required=False,
        missing_value='')

    breaking_news = zope.schema.Bool(
        title=_('video-breaking-news', default='Breaking news'),
        default=False)

    has_recensions = zope.schema.Bool(
        title=_('Has recension content'),
        default=False)

    expires = zope.schema.Datetime(
        title=_('Video expires on'),
        required=False,
        readonly=True,
        default=None)

    date_first_released = zope.schema.Datetime(
        title=_('First released'),
        required=False,
        readonly=True,
        default=None)

    date_created = zope.schema.Datetime(
        title=_('Created on'),
        required=False,
        readonly=True,
        default=None)

    date_last_modified = zope.schema.Datetime(
        title=_('last modified'),
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


