from unittest.mock import Mock

import zope.interface.verify

from zeit.content.audio.interfaces import Podcast, PodcastSource
from zeit.content.audio.testing import AudioBuilder, FunctionalTestCase
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.audio.audio
import zeit.content.image.interfaces


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
            'https://feeds.example.com/aRDC72E_',
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


class SpeechTest(FunctionalTestCase):
    def test_create_tts_audio(self):
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        uuid = zeit.cms.content.interfaces.IUUID(article)
        audio = zeit.content.audio.audio.Audio()
        audio.audio_type = 'tts'
        tts = zeit.content.audio.interfaces.ISpeechInfo(audio)
        tts.article_uuid = uuid.shortened
        tts.preview_url = 'https://example-preview-url.bert'
        tts.checksum = '123foo'
        audio = self.repository['audio'] = audio
        speechinfo = zeit.content.audio.interfaces.ISpeechInfo(audio)
        self.assertEqual(audio.audio_type, 'tts')
        self.assertEqual(speechinfo.article_uuid, uuid.shortened)
        self.assertEqual(speechinfo.preview_url, 'https://example-preview-url.bert')
        self.assertTrue(speechinfo.checksum, '123foo')
