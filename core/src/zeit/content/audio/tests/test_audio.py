import zeit.content.audio.audio
import zeit.content.audio.testing


class TestAudio(zeit.content.audio.testing.FunctionalTestCase):

    def test_audio_has_properties(self):
        audio = zeit.content.audio.audio.Audio()
        audio.title = 'foo'
        audio.url = 'https://foo.bah/1234/episode-mp3'
        audio.episode_id = '12-34'
        self.assertEqual(audio.title, 'foo')
        self.assertEqual(audio.url, 'https://foo.bah/1234/episode-mp3')
        self.assertEqual(audio.episode_id, '12-34')
