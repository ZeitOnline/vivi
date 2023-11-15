from zope.testbrowser.browser import LinkNotFoundError

from zeit.content.audio.audio import Audio, PodcastEpisodeInfo
from zeit.content.audio.interfaces import Podcast
import zeit.content.audio.testing


class AudioObjectDetails(zeit.content.audio.testing.BrowserTestCase):
    def create_audio(self):
        audio = Audio()
        audio.title = 'mytitle'
        audio.url = 'http://example.com/cats.mp3'
        audio.duration = 123
        audio.audio_type = 'podcast'
        podcast = Podcast('cat-jokes-pawdcast', 'Cat Jokes Pawdcast', '1234', 'Jokes about cats')
        PodcastEpisodeInfo(audio).podcast = podcast

        self.repository['audio'] = audio
        return audio

    def test_displays_details(self):
        audio = self.create_audio()
        b = self.browser
        b.open('/repository/audio/@@object-details')
        self.assert_ellipsis(
            f'...<li class="teaser_title" title="{audio.title}">{audio.title}</li>...'
            '...<dt>Duration</dt>...'
            '...<dd>02:03</dd>...'
            '...<dt>Type</dt>...'
            '...<dd>podcast</dd>...'
            '...<dt>Podcast</dt>...'
            '...<dd>Cat Jokes Pawdcast</dd>...'
            f'...<a target="_blank" href="{audio.url}">Play</a>...',
            b.contents,
        )

    def test_displays_additional_info_only_if_available(self):
        audio = Audio()
        audio.title = 'mytitle'
        audio.audio_type = 'tts'
        self.repository['audio'] = audio
        b = self.browser
        b.open('/repository/audio/@@object-details')
        self.assert_ellipsis(
            '...<li class="teaser_title" title="mytitle">mytitle</li>...', b.contents
        )
        assert (
            'Duration:' not in b.contents
        ), 'Duration should not be displayed without duration set'
        assert (
            'open-audio object-link' not in b.contents
        ), 'Play should not be displayed without url'
        assert (
            'Podcast:' not in b.contents
        ), 'Podcast should not be displayed without audio_type set to podcast'

    def test_cannot_delete_if_permissions_missing(self):
        self.create_audio()
        b = self.browser
        b.open('/repository/audio')
        with self.assertRaises(LinkNotFoundError):
            assert not b.getLink(url='@@delete.html')

    def test_duration(self):
        test_cases = [
            (1500, '25:00'),
            (7512, '02:05:12'),
        ]
        audio = self.create_audio()
        for duration, expected in test_cases:
            audio.duration = duration
            self.repository['audio'] = audio
            b = self.browser
            b.open('/repository/audio/@@object-details')
            self.assert_ellipsis(f'...<dd>{expected}</dd>...', b.contents)
