from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zope.interface
import zope.schema


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/brightcove'


class IAPIConnection(zope.interface.Interface):
    """Brightcove API connection, deprecated in 2017."""


class ICMSAPI(zope.interface.Interface):
    """Brightcove CMS-API connection."""

    def get_video(id):
        """Returns the video metadata as a dict.
        If no video was found by Brightcove, returns None.
        """

    def get_video_sources(id):
        """Returns a list of dicts with data about video sources/renditions."""

    def update_video(bcvideo):
        """Updates the video metadata."""

    def get_playlist(id):
        """Returns the playlist metadata as a dict.
        If no playlist was found by Brightcove, returns None.
        """

    def get_all_playlists():
        """Returns a list of dicts with the metadata of all playlists."""


class ISession(zope.interface.Interface):
    """Integrates ICMSAPI with the ``transaction`` module.
    Clients should call ``zeit.brightcove.session.get()`` to get the current
    thread-local Session instance, which they then can use to make changes.

    Note that the Brightcove API does not support transactions, so we muddle
    through by trying to commit last in the 2PC protocol. (This also means,
    if you update multiple videos and the first errors out, the other ones
    will NOT be updated.)
    """

    def update_video(bcvideo):
        """Updates the video metadata (on transaction commit)."""


class IBrightcoveObject(zope.interface.Interface):
    """A representation of an object as stored in Brightcove."""


class IBrightcoveContent(zeit.cms.interfaces.ICMSContent):

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
    """A video.

    The schema must contain all fields that use
    ``zeit.brightcove.converter.mapped``, since the mapping will try to read
    default values from the schema.

    """

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

    commentsAllowed = zope.schema.Bool(
        title=_("Comments allowed"),
        default=True)

    commentsPremoderate = zope.schema.Bool(
        title=_("Comments premoderate"),
        default=False)

    ignore_for_update = zope.schema.Bool(
        title=_("Ignore for update"),
        default=False)

    dailyNewsletter = zope.schema.Bool(
        title=_("Daily newsletter"),
        default=False)

    banner = zope.schema.Bool(
        title=_("Banner"),
        default=True)

    breaking_news = zope.schema.Bool(
        title=_('Breaking news'),
        default=False)

    video_still_copyright = zope.schema.TextLine(
        title=_('Video still copyright'),
        required=False)


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


class IRepository(zope.interface.Interface):
    """legacy interface."""


class IUpdate(zope.interface.Interface):
    """Update a Brightcove object from Brightcove."""
