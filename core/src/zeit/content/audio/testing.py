from functools import partialmethod
from typing import Optional, TypeVar
import importlib.resources

from zeit.cms.repository.interfaces import IRepository
from zeit.content.audio.audio import Audio
from zeit.content.audio.interfaces import IPodcastEpisodeInfo, ISpeechInfo, Podcast
import zeit.cms.testing
import zeit.workflow.testing


T = TypeVar('T')  # Can be anything

product_config = """
<product-config zeit.content.audio>
   podcast-source file://{here}/tests/fixtures/podcasts.xml
</product-config>
""".format(here=importlib.resources.files(__package__))

CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    product_config,
    bases=(
        zeit.workflow.testing.CONFIG_LAYER,
        zeit.cms.testing.CONFIG_LAYER,
    ),
)

ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class AudioBuilder:
    """Builds an audio object with default values for all attributes.
    Methods with name `with_<attribute>` can be used to set the value.

    Example:
        >>> AudioBuilder().with_title('foo').build()
    """

    def __init__(self):
        self.attributes = {
            'audio': {
                'title': 'Pawdcast',
                'external_id': '1234',
                'url': 'http://example.com/cats.mp3',
                'duration': 123,
                'audio_type': 'podcast',
            },
            'podcast': {
                'episode_nr': 1,
                'url_ad_free': 'http://simplecast.com/adfree.mp3',
                'summary': 'lorem ipsum',
                'notes': '<p>dolor <b>sit</b> amet</p>',
                'is_published': True,
                'dashboard_link': 'http://simplecast.com/pawdcast',
                'podcast': Podcast(
                    # see zeit/content/audio/tests/fixtures/podcasts.xml
                    'cat-jokes-pawdcast',
                ),
            },
            'tts': {
                'article_uuid': 'a89ce2e3-4887-466a-a52e-edc6b9802ef9',
                'preview_url': 'https://example-preview-url.bert',
                'checksum': '123foo',
            },
        }

    def with_attribute(self, attribute_name: str, value: T):
        for key in self.attributes:
            if attribute_name in self.attributes[key]:
                self.attributes[key][attribute_name] = value
                return self
        raise ValueError(f'Unknown attribute {attribute_name}')

    def build(self, repository: Optional[IRepository] = None) -> Audio:
        audio = Audio()
        audio_type = self.attributes['audio']['audio_type']
        for attribute, value in self.attributes['audio'].items():
            setattr(audio, attribute, value)
        if audio_type == 'podcast':
            episode = IPodcastEpisodeInfo(audio)
            for attribute, value in self.attributes[audio_type].items():
                setattr(episode, attribute, value)
        if audio_type == 'tts':
            tts = ISpeechInfo(audio)
            audio.external_id = ''
            for attribute, value in self.attributes[audio_type].items():
                setattr(tts, attribute, value)
        if repository is not None:
            repository['audio'] = audio

        return audio


# Add methods for each attribute to AudioBuilder
for key in AudioBuilder().__dict__['attributes']:
    for attribute in AudioBuilder().__dict__['attributes'][key]:
        setattr(
            AudioBuilder, f'with_{attribute}', partialmethod(AudioBuilder.with_attribute, attribute)
        )
