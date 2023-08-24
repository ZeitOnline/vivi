import requests_mock
import zope.component
import zeit.simplecast.interfaces
import zeit.simplecast.testing

JSON = {
    "title": "Cat Jokes Pawdcast",
    "id": "1234",
    "audio_file_url": (
        "https://injector.simplecastaudio.com/5678/episodes/1234/audio"
        "/128/default.mp3?awCollectionId=5678&awEpisodeId=1234"),
    "ad_free_audio_file_url": None,
    "duration": 666,
}


class TestSimplecastAPI(zeit.simplecast.testing.FunctionalTestCase):

    def test_audio_has_url(self):
        m_simple = requests_mock.Mocker()
        episode_id = '1234'
        m_simple.get(
            f'https://testapi.simplecast.com/episodes/{episode_id}', json=JSON)
        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        with m_simple:
            (url, duration, title) = simplecast.get_episode(episode_id)
            assert url == (
                'https://injector.simplecastaudio.com/5678/episodes/'
                '1234/audio/128/default.mp3?awCollectionId=5678'
                '&awEpisodeId=1234')
            assert duration == 666

    def test_episode_not_found_breaks(self):
        m_simple = requests_mock.Mocker()
        episode_id = '1234'
        m_simple.get(
            f'https://testapi.simplecast.com/episodes/{episode_id}',
            json={},
            status_code=404)
        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)

        with m_simple:
            with self.assertRaises(KeyError):
                simplecast.get_episode(episode_id)
