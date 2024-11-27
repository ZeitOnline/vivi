import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
import zeit.cms.content.contentsource
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.retresco.interfaces


class AudioTypeSource(zeit.cms.content.sources.SimpleFixedValueSource):
    """
    Identify audio types without inspecting live object.
    For example to be used in zeit.web templates.
    """

    values = {
        'podcast': _('Podcast'),
        'tts': _('Text to Speech'),
        'premium': _('Premium Audio'),
        'custom': _('Custom Audio'),
    }


class IAudio(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.content.interfaces.IXMLContent,
    zeit.retresco.interfaces.ISkipEnrich,
):
    """
    Basic playable audio containing minimum required information
    for ZEIT audio players.
    """

    title = zope.schema.TextLine(title=_('Title'))
    external_id = zope.schema.TextLine(title=_('External Id'))
    url = zope.schema.URI(title=_('URL'), required=False)
    duration = zeit.cms.content.field.DurationField(title=_('Duration'), min=0, required=False)
    audio_type = zope.schema.Choice(title=_('Type'), readonly=True, source=AudioTypeSource())


class PodcastTypeSource(zeit.cms.content.sources.SimpleFixedValueSource):
    """
    Define podcast types. This is especially interesting for third party platforms
    or podcatchers.
    """

    values = {
        'serial': _('Serial'),
        'episodic': _('Episodic'),
        'episodic_seasons': _('Episodic seasons'),
    }


class IPodcast(zope.interface.Interface):
    id = zope.interface.Attribute('id')
    title = zope.interface.Attribute('title')
    external_id = zope.interface.Attribute('external_id')
    subtitle = zope.interface.Attribute('subtitle')
    color = zope.interface.Attribute('color')
    image = zope.schema.URI(title=_('show art'))
    distribution_channels = zope.interface.Attribute('distribution_channels')
    feed = zope.schema.URI(title=_('feed'))
    explicit = zope.schema.Bool(title=_('Explicit'), readonly=True, default=False)
    author = zope.interface.Attribute('author')
    category = zope.interface.Attribute('category')
    podcast_type = zope.schema.Choice(title=_('Type'), readonly=True, source=PodcastTypeSource())


class Podcast(zeit.cms.content.sources.AllowedBase):
    def __init__(
        self,
        id,
        title=None,
        external_id=None,
        subtitle=None,
        color=None,
        image=None,
        distribution_channels=None,
        feed=None,
        explicit=None,
        author=None,
        category=None,
        podcast_type=None,
    ):
        super().__init__(id, title, available=None)
        self.external_id = external_id
        self.subtitle = subtitle
        self.color = color
        self.image = image
        #: mapping of distribution channel (itunes, spotify, etc.) to url
        self.distribution_channels = distribution_channels
        # For parallel use of podcast hosts
        self.feed = feed
        self.explicit = explicit
        self.author = author
        self.category = category
        self.podcast_type = podcast_type

    def __eq__(self, other):
        return (
            zope.security.proxy.isinstance(other, self.__class__)
            and self.id == other.id
            and self.title == other.title
            and self.external_id == other.external_id
            and self.subtitle == other.subtitle
            and self.color == other.color
            and self.image == other.image
            and self.distribution_channels == other.distribution_channels
            and self.feed == other.feed
            and self.explicit == other.explicit
            and self.author == other.author
            and self.category == other.category
            and self.podcast_type == other.podcast_type
        )


class PodcastSource(zeit.cms.content.sources.ObjectSource, zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.audio'
    config_url = 'podcast-source'
    default_filename = 'podcasts.xml'
    attribute = 'id'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = {}
        tree = self._get_tree()
        for node in tree.iterchildren('*'):
            podcast = self._create_podcast(node)
            result[podcast.id] = podcast
        return result

    def _create_podcast(self, node):
        channels = node.iterchildren('distribution_channel')
        distribution_channels = {x.get('id'): x.get('href') for x in channels}
        podcast = Podcast(
            node.get(self.attribute),
            node.get('title'),
            node.get('external_id'),
            node.get('subtitle'),
            node.get('color'),
            node.get('image'),
            distribution_channels,
            node.get('feed'),
            bool(node.get('explicit')),
            node.get('author'),
            node.get('category'),
            node.get('podcast_type'),
        )
        return podcast


class IPodcastEpisodeInfo(zope.interface.Interface):
    """Additional Audioinformation for podcast episodes."""

    podcast = zope.schema.Choice(
        title=_('Podcast Serie'), source=PodcastSource(), readonly=True, required=False
    )
    podcast_id = zope.schema.TextLine(title=_('External Podcast Id'), required=False, readonly=True)
    episode_nr = zope.schema.Int(title=_('Episode No'), readonly=True, required=False)
    url_ad_free = zope.schema.URI(title=_('URL ad-free'), readonly=True, required=False)
    summary = zope.schema.Text(title=_('Episode Summary'), required=False, readonly=True)
    notes = zope.schema.Text(title=_('Episode Notes'), required=False, readonly=True)
    is_published = zope.schema.Bool(title=_('Is Published'), readonly=True, default=False)
    dashboard_link = zope.schema.URI(title=_('Dashboard Link'), required=False)


class AudioSource(zeit.cms.content.contentsource.CMSContentSource):
    name = 'audio'
    check_interfaces = (IAudio,)


class IAudioReferences(zope.interface.Interface):
    items = zope.schema.Tuple(
        title=_('AudioReferences'), value_type=zope.schema.Choice(source=AudioSource())
    )

    def add(audio: IAudio):
        pass

    def get_by_type(audio_type: str) -> [IAudio]:
        pass


class ISpeechInfo(zope.interface.Interface):
    article_uuid = zope.schema.ASCIILine(
        title='Article uuid',
        description='The uuid of the content object',
        required=False,
        readonly=True,
    )
    preview_url = zope.schema.URI(title=_('Preview URL'), required=False, readonly=True)

    checksum = zope.schema.ASCIILine(title=_('Speechbert Checksum'), required=False, readonly=True)
