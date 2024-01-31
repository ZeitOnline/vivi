from zope.testbrowser.browser import LinkNotFoundError

from zeit.content.audio.testing import AudioBuilder, BrowserTestCase


class AudioObjectDetails(BrowserTestCase):
    def test_displays_details(self):
        audio = AudioBuilder().build(self.repository)
        b = self.browser
        b.open('/repository/audio/@@object-details')
        self.assert_ellipsis(
            f'...<li class="teaser_title" title="{audio.title}">{audio.title}</li>...'
            '...<dt>Duration</dt>...'
            '...<dd>02:03</dd>...'
            '...<dt>Type</dt>...'
            '...<dd>Podcast</dd>...'
            '...<dt>Podcast</dt>...'
            '...<dd>Cat Jokes Pawdcast</dd>...'
            f'...<a target="_blank" href="{audio.url}">Play</a>...',
            b.contents,
        )

    def test_displays_additional_info_only_if_available(self):
        AudioBuilder().with_duration(0).with_url('').with_title('mytitle').with_audio_type(
            'tts'
        ).build(self.repository)
        b = self.browser
        b.open('/repository/audio/@@object-details')
        self.assert_ellipsis(
            '...<li class="teaser_title" title="mytitle">mytitle</li>...', b.contents
        )
        assert 'Duration' not in b.contents, 'Duration should not be displayed without duration set'
        assert (
            'open-audio object-link' not in b.contents
        ), 'Play should not be displayed without url'
        assert (
            'Podcast' not in b.contents
        ), 'Podcast should not be displayed without audio_type set to podcast'

    def test_cannot_delete_if_permissions_missing(self):
        AudioBuilder().build(self.repository)
        b = self.browser
        b.open('/repository/audio')
        with self.assertRaises(LinkNotFoundError):
            assert not b.getLink(url='@@delete.html')

    def test_duration(self):
        test_cases = [
            (1500, '25:00'),
            (7512, '02:05:12'),
        ]
        audio = AudioBuilder().build(self.repository)
        for duration, expected in test_cases:
            audio.duration = duration
            self.repository['audio'] = audio
            b = self.browser
            b.open('/repository/audio/@@object-details')
            self.assert_ellipsis(f'...<dd>{expected}</dd>...', b.contents)
