import requests_mock
import zope.component
import zeit.cms.repository.folder
import zeit.content.audio.audio
import zeit.simplecast.interfaces
import zeit.simplecast.testing


class TestSimplecastAPI(zeit.simplecast.testing.FunctionalTestCase):

    def create_audio(self, json):
        audio = zeit.content.audio.audio.Audio()
        audio.title = json['title']
        audio.episode_id = json['id']
        audio.url = json['audio_file_url']
        self.repository['podcasts'] = zeit.cms.repository.folder.Folder()
        self.repository['podcasts']['2023-08'] = zeit.cms.repository.folder.Folder()
        self.repository['podcasts']['2023-08'][audio.episode_id] = audio

    def setUp(self):
        super().setUp()
        self.simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)

    def test_simplecast_yields_episode_info(self):
        m_simple = requests_mock.Mocker()
        episode_id = "1234"
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{episode_id}",
            json=self.episode_info)
        with m_simple:
            result = self.simplecast.fetch_episode(
                episode_id)
            self.assertEqual(result, self.episode_info)

    def test_simplecast_gets_podcast_folder(self):
        container = self.simplecast.folder(self.episode_info["created_at"])
        self.assertEqual(container, self.repository["podcasts"]["2023-08"])

    def test_create_episode(self):
        m_simple = requests_mock.Mocker()
        episode_id = '1234'
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{episode_id}",
            json=self.episode_info)
        with m_simple:
            self.simplecast.create_episode(episode_id)
        episode = self.repository['podcasts']['2023-08'][episode_id]
        self.assertEqual('podcast', episode.audio_type)
        self.assertEqual('Cat Jokes Pawdcast', episode.title)
        self.assertEqual(episode_id, episode.external_id)
        self.assertEqual(
            'Cat Jokes Pawdcast',
            zeit.content.audio.interfaces.IPodcastEpisodeInfo(episode).podcast.title)

    def test_update_episode(self):
        episode_id = '1234'
        self.create_audio(self.episode_info)
        self.assertEqual(
            'Cat Jokes Pawdcast',
            self.repository['podcasts']['2023-08'][episode_id].title)
        json = self.episode_info.copy()
        json['title'] = "Cat Jokes Pawdcast - Folge 2"
        m_simple = requests_mock.Mocker()
        episode_id = '1234'
        self.repository.connector.search_result = [(
            'http://xml.zeit.de/podcasts/2023-08/1234')]
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{episode_id}",
            json=json)
        with m_simple:
            self.simplecast.update_episode(episode_id)
        episode = self.repository['podcasts']['2023-08'][episode_id]
        self.assertEqual('Cat Jokes Pawdcast - Folge 2', episode.title)

    def test_delete_episode(self):
        episode_id = '1234'
        self.create_audio(self.episode_info)
        self.assertTrue(
            zeit.content.audio.interfaces.IAudio.providedBy(
                self.repository['podcasts']['2023-08'][episode_id]))
        self.repository.connector.search_result = [(
            'http://xml.zeit.de/podcasts/2023-08/1234')]
        self.simplecast.delete_episode(episode_id)
        self.assertNotIn(episode_id, self.repository['podcasts']['2023-08'])
