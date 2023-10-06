from zeit.content.audio.interfaces import Podcast
from zeit.content.audio.audio import Audio, PodcastEpisodeInfo
import zeit.content.audio.testing


class AudioObjectDetails(zeit.content.audio.testing.BrowserTestCase):

    def test_displays_details(self):
        audio = Audio()
        audio.title = 'mytitle'
        audio.url = 'http://example.com/cats.mp3'
        audio.duration = 123
        audio.audio_type = 'podcast'
        podcast = Podcast(
            'cat-jokes-pawdcast', 'Cat Jokes Pawdcast', '1234', 'Jokes about cats')
        PodcastEpisodeInfo(audio).podcast = podcast

        self.repository['audio'] = audio
        b = self.browser
        b.open('/repository/audio/@@object-details')
        self.assert_ellipsis(
            f'...<li class="teaser_title" title="{audio.title}">{audio.title}</li>...'
            '...<dt>Duration</dt>...'
            '...<dd>2:03</dd>...'
            '...<dt>Type</dt>...'
            '...<dd>podcast</dd>...'
            '...<dt>Podcast</dt>...'
            '...<dd>Cat Jokes Pawdcast</dd>...'
            f'...<a target="_blank" href="{audio.url}">Play</a>...',
            b.contents
        )

    def test_displays_additional_info_only_if_available(self):
        audio = Audio()
        audio.title = 'mytitle'
        audio.audio_type = 'tts'
        self.repository['audio'] = audio
        b = self.browser
        b.open('/repository/audio/@@object-details')
        self.assert_ellipsis(
            '...<li class="teaser_title" title="mytitle">mytitle</li>...',
            b.contents
        )
        assert 'Duration:' not in b.contents, 'Duration should not be displayed without duration set'
        assert 'open-audio object-link' not in b.contents, 'Play should not be displayed without url'
        assert 'Podcast:' not in b.contents, 'Podcast should not be displayed without audio_type set to podcast'
