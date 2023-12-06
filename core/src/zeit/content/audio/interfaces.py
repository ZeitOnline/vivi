from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE

import zeit.cms.content.contentsource
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zope.interface
import zope.schema


class AudioTypeSource(zeit.cms.content.sources.SimpleFixedValueSource):
    """
    Identify audio types without inspecting live object.
    For example to be used in zeit.web templates.
    """

    values = {
        'podcast': _('Podcast'),
        'tts': _('Text to Speech'),
        'premium': _('Premium Audio'),
    }


class IAudio(zeit.cms.content.interfaces.ICommonMetadata, zeit.cms.content.interfaces.IXMLContent):
    """
    Basic playable audio containing minimum required information
    for ZEIT audio players.
    """

    title = zope.schema.TextLine(title=_('Title'))
    external_id = zope.schema.TextLine(title=_('External Id'))
    url = zope.schema.URI(title=_('URL'), required=False)
    duration = zeit.cms.content.field.DurationField(title=_('Duration'), min=0, required=False)
    audio_type = zope.schema.Choice(title=_('Type'), readonly=True, source=AudioTypeSource())


class IPodcast(zope.interface.Interface):
    id = zope.interface.Attribute('id')
    title = zope.interface.Attribute('title')
    external_id = zope.interface.Attribute('external_id')
    subtitle = zope.interface.Attribute('subtitle')
    color = zope.interface.Attribute('color')
    image = zope.schema.URI(title=_('show art'))
    distribution_channels = zope.interface.Attribute('distribution_channels')


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
        podigee_id=None,
    ):
        super().__init__(id, title, available=None)
        self.external_id = external_id
        self.subtitle = subtitle
        self.color = color
        self.image = image
        #: mapping of distribution channel (itunes, spotify, etc.) to url
        self.distribution_channels = distribution_channels
        # For parallel use of podcast hosts
        self.podigee_id = podigee_id

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
            and self.podigee_id == other.podigee_id
        )


class PodcastSource(zeit.cms.content.sources.ObjectSource, zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.audio'
    config_url = 'podcast-source'
    default_filename = 'podcasts.xml'
    attribute = 'id'

    class source_class(zeit.cms.content.sources.ObjectSource.source_class):
        def find_by_property(self, property_name, value):
            return self.factory.find_by_property(self.context, property_name, value)

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
            podigee_id=node.get('podigee_id'),
        )
        podcast.distribution_channels = distribution_channels
        return podcast

    def find_by_property(self, context, property_name, value):
        for item in self._values().values():
            if getattr(item, property_name) == value:
                return item
        return None


class IPodcastEpisodeInfo(zope.interface.Interface):
    """Additional Audioinformation for podcast episodes."""

    podcast = zope.schema.Choice(title=_('Podcast Serie'), source=PodcastSource(), readonly=True)
    podcast_id = zope.schema.TextLine(title=_('External Podcast Id'), required=False, readonly=True)
    episode_nr = zope.schema.Int(title=_('Episode No'), readonly=True)
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
