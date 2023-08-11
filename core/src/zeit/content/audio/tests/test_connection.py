import requests_mock
import zope.component
import zeit.content.audio.audio
import zeit.content.audio.testing


class TestSimplecastAPI(zeit.content.audio.testing.FunctionalTestCase):

    def test_audio_has_url(self):
        m_simple = requests_mock.Mocker()
        episode_id = '1234'
        m_simple.get(
            f'https://testapi.simplecast.com/episodes/{episode_id}', json=self.json)
        simplecast = zope.component.getUtility(
            zeit.content.audio.interfaces.ISimplecast)
        (url, duration) = simplecast.get_episode(episode_id)
        assert url == 'https://injector.simplecastaudio.com/5678/episodes/1234/audio/128/default.mp3?awCollectionId=5678&awEpisodeId=1234'
        assert duration == 666