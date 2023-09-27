from unittest.mock import Mock

from zeit.content.audio.interfaces import PodcastSource, Podcast

import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.audio.interfaces
import zeit.content.audio.audio
import zeit.content.audio.testing
import zope.interface.verify


class PodcastSourceTest(zeit.content.audio.testing.FunctionalTestCase):

    def test_podcast_source(self):
        podcast_source = PodcastSource().factory
        context = Mock()
        values = podcast_source.getValues(context)
        assert len(values) == 1
        distribution_channels = {
            'itunes': 'http://example.com/itunes',
            'google': 'http://example.com/google'
        }
        podcast = Podcast(
            'cat-jokes-pawdcast', 'Cat Jokes Pawdcast', 'c3161c7d',
            'A podcast of cat jokes', distribution_channels, 'asdf-1234')
        assert values[0] == podcast

    def test_audio_provides_ICommonMetadata(self):
        audio = zeit.content.audio.audio.Audio()
        zope.interface.verify.verifyObject(
            zeit.cms.content.interfaces.ICommonMetadata, audio)
        # Returns default values for not applicable properties
        self.assertEqual((), audio.authorships)
