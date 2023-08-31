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
        self.assertEqual(container, self.repository["podcasts"]["2023-08"])

    def test_find_episode_from_connector(self):
        """After an `episode_deleted` event, information about the
        episode can not be fetched from the simplecast api anymore, yields 404
        """
        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        episode = simplecast.find_existing_episode(self.episode_info["id"])
        self.assertFalse(episode)

        container = simplecast.folder("2023-08-31T13:51:00-01:00")
        zeit.content.audio.audio.add_audio(
            container, self.episode_info)

        self.repository.connector.search_result = [(
            'http://xml.zeit.de/podcasts/2023-08/'
            'b44b1838-4ff4-4c29-ba1c-9c4f4b863eac')]

        episode = simplecast.find_existing_episode(self.episode_info["id"])
        self.assertTrue(
            zeit.content.audio.interfaces.IAudio.providedBy(episode))
        self.assertEqual(self.episode_info["title"], episode.title)
        self.assertEqual(self.episode_info["audio_file_url"], episode.url)
