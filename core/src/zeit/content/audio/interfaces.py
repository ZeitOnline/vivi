from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE

import zeit.cms.content.contentsource
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


class IAudio(zeit.cms.content.interfaces.ICommonMetadata,
             zeit.cms.content.interfaces.IXMLContent):
    """
    Basic playable audio containing minimum required information
    for ZEIT audio players.
    """

    title = zope.schema.TextLine(title=_('Title'))
    external_id = zope.schema.TextLine(title=_('External Id'))
    url = zope.schema.URI(title=_('URL'), required=False)
    duration = zope.schema.Int(title=_('Duration'), required=False)
    audio_type = zope.schema.Choice(
        title=_('Typ'),
        readonly=True,
        default='podcast',
        source=AudioTypeSource())


class IPodcast(zope.interface.Interface):

    id = zope.interface.Attribute('id')
    title = zope.interface.Attribute('title')
    external_id = zope.interface.Attribute('external_id')
    subtitle = zope.interface.Attribute('subtitle')
    distribution_channels = zope.interface.Attribute('distribution_channels')


class Podcast(zeit.cms.content.sources.AllowedBase):

    def __init__(
            self, id, title,
            external_id, subtitle, distribution_channels=None):
        super().__init__(id, title, available=None)
        self.external_id = external_id
        self.subtitle = subtitle
        #: mapping of distribution channel (itunes, spotify, etc.) to url
        self.distribution_channels = distribution_channels


class PodcastSource(zeit.cms.content.sources.ObjectSource,
                    zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.audio'
    config_url = 'podcast-source'
    default_filename = 'podcasts.xml'
    attribute = 'id'

    class source_class(zeit.cms.content.sources.ObjectSource.source_class):

        def find_by_property(self, property_name, value):
            return self.factory.find_by_property(
                self.context, property_name, value)

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
        distribution_channels = {
            x.get('id'): x.get('href') for x in channels
        }
        podcast = Podcast(
            node.get(self.attribute),
            node.get('title'),
            node.get('external_id'),
            node.get('subtitle'))
        podcast.distribution_channels = distribution_channels
        return podcast

    def find_by_property(self, context, property_name, value):
        for item in self._values().values():
            if getattr(item, property_name) == value:
                return item
        return None


class IPodcastEpisodeInfo(zope.interface.Interface):
    """Additional Audioinformation for podcast episodes."""
    podcast = zope.schema.Choice(
        title=_('Podcast Serie'),
        source=PodcastSource(),
        readonly=True)
    # XXX reference image group instead of URL
    image = zope.schema.URI(
        title=_('Remote Image URL'),
        readonly=True)
    episode_nr = zope.schema.Int(
        title=_('Episode No'),
        readonly=True)
    summary = zope.schema.Text(
        title=_('Episode Summary'),
        readonly=True)
    notes = zope.schema.Text(
        title=_('Episode Notes'),
        readonly=True)


class AudioSource(zeit.cms.content.contentsource.CMSContentSource):
    name = "audio"
    check_interfaces = (IAudio,)


class IAudios(zope.interface.Interface):
    items = zope.schema.Tuple(
        title=_('Audios'),
        value_type=zope.schema.Choice(source=AudioSource()))
