from unittest.mock import Mock

from zeit.content.audio.interfaces import PodcastSource, Podcast
from zeit.content.audio.testing import AudioBuilder, FunctionalTestCase

import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.audio.audio
import zeit.content.image.interfaces
import zope.interface.verify


class PodcastSourceTest(FunctionalTestCase):
    def test_podcast_source(self):
        podcast_source = PodcastSource().factory
        context = Mock()
        values = podcast_source.getValues(context)
        assert len(values) == 1
        distribution_channels = {
            'itunes': 'http://example.com/itunes',
            'google': 'http://example.com/google',
        }
        podcast = Podcast(
            'cat-jokes-pawdcast',
            'Cat Jokes Pawdcast',
            '1234',
            'A podcast of cat jokes',
            'e5ded8',
            'http://xml.zeit.de/2006/DSC00109_2.JPG',
            distribution_channels,
            'podigee-1234',
        )
        assert values[0] == podcast

    def test_audio_provides_ICommonMetadata(self):
        audio = zeit.content.audio.audio.Audio()
        zope.interface.verify.verifyObject(zeit.cms.content.interfaces.ICommonMetadata, audio)
        # Returns default values for not applicable properties
        self.assertEqual((), audio.authorships)

    def test_get_podcast_image(self):
        audio = AudioBuilder().build(self.repository)
        images = zeit.content.image.interfaces.IImages(audio)
        assert images.image.uniqueId == 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        assert (
            images.fill_color == 'e5ded8'
        ), 'Fill color should match color audio/tests/fixtures/podcasts.xml'
