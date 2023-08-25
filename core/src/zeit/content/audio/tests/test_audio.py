import zope.component
import zeit.content.audio.audio
import zeit.content.audio.testing


class TestAudio(zeit.content.audio.testing.FunctionalTestCase):

    def test_audio_has_properties(self):
        audio = zeit.content.audio.audio.Audio()
        audio.title = 'foo'
        audio.url = 'https://foo.bah/1234/episode-mp3'
        audio.episodeId = '12-34'
        self.assertEqual(audio.title, 'foo')
        self.assertEqual(audio.url, 'https://foo.bah/1234/episode-mp3')
        self.assertEqual(audio.episodeId, '12-34')

    def test_audio_is_saved_in_container(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        self.assertNotIn('podcast-audio', repository.keys())
        zeit.content.audio.audio.audio_container(create=True)
        self.assertIn('podcast-audio', repository.keys())
