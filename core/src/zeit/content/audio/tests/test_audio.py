import zeit.content.audio.audio
import zeit.content.audio.testing


class TestAudio(zeit.content.audio.testing.FunctionalTestCase):

    def test_audio_has_properties(self):
        audio = zeit.content.audio.audio.Audio()
        audio.title = 'foo'
        audio.url = 'https://foo.bah/1234/episode-mp3'
        audio.episode_id = '12-34'
        audio.serie = 'was gibts'
        audio.duration = 123
        audio.image = 'https://test-ing.com/test-image'
        self.assertEqual(audio.title, 'foo')
        self.assertEqual(audio.url, 'https://foo.bah/1234/episode-mp3')
        self.assertEqual(audio.episode_id, '12-34')
        self.assertEqual(audio.duration, 123)
        self.assertEqual(audio.image, 'https://test-ing.com/test-image')
        self.assertEqual(audio.serie, 'was gibts')
