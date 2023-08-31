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
    "created_at": "2023-08-31T13:51:00-01:00",
    "duration": 666,
}


class TestSimplecastAPI(zeit.simplecast.testing.FunctionalTestCase):

    def test_simplecast_yields_episode_info(self):
        m_simple = requests_mock.Mocker()
        episode_id = "1234"
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{episode_id}",
            json=JSON)
        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        with m_simple:
            result = simplecast.fetch_episode(episode_id)
            self.assertEqual(result, JSON)

    def test_simplecast_gets_podcast_folder(self):
        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        container = simplecast.folder(JSON["created_at"])
        self.assertEqual(container, self.repository['podcasts']['2023-08'])
