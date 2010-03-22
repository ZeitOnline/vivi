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


class IBrightcoveContent(zeit.cms.interfaces.ICMSContent):

    id = zope.schema.Int(
        title=_('Id'),
        readonly=True)

    title = zope.schema.TextLine(
        title=_("Title"))

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)

    thumbnail = zope.schema.URI(
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
        required=False)

    subtitle = zope.schema.Text(
        title=_("Video subtitle"),
        required=False,
        max_length=5000)

    ressort = zope.schema.Choice(
        title=_("Ressort"),
        source=zeit.cms.content.sources.NavigationSource())

    serie = zope.schema.Choice(
        title=_("Serie"),
        source=zeit.cms.content.sources.SerieSource(),
        required=False)

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

    banner = zope.schema.Bool(
        title=_("Banner"),
        default=False)

    banner_id = zope.schema.TextLine(
        title=_('Banner id'),
        required=False)

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


class IPlaylist(IBrightcoveContent):
    """A playlist."""


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
        source=videoSource)

    video_2 = zope.schema.Choice(
        title=_('Video 2'),
        required=False,
        source=videoSource)
