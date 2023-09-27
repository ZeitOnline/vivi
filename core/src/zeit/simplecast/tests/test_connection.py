from unittest import mock

from zeit.content.audio.interfaces import IPodcastEpisodeInfo, IAudio
from zeit.content.audio.workflow import AudioWorkflow, PodcastWorkflow

import pytest

import requests_mock
import zope.component

import zeit.cms.repository.folder
import zeit.content.audio.audio
import zeit.simplecast.interfaces
import zeit.simplecast.testing

import zeit.cms.workflow.interfaces
import zeit.workflow.asset


class TestSimplecastAPI(zeit.simplecast.testing.FunctionalTestCase):

    def create_audio(self, json):
        with mock.patch.object(self.simplecast, '_fetch_episode') as request:
            request.return_value = json
            self.simplecast.create_episode(json['id'])
        self.repository.connector.search_result = [(f'http://xml.zeit.de/podcasts/2023-08/{json["id"]}')]

    def setUp(self):
        super().setUp()
        self.simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)

    def test_simplecast_yields_episode_info(self):
        m_simple = requests_mock.Mocker()
        episode_id = self.episode_info["id"]
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{episode_id}",
            json=self.episode_info)
        with m_simple:
            result = self.simplecast._fetch_episode(
                episode_id)
            self.assertEqual(result, self.episode_info)

    def test_simplecast_gets_podcast_folder(self):
        container = self.simplecast.folder(self.episode_info["created_at"])
        self.assertEqual(container, self.repository["podcasts"]["2023-08"])

    def test_create_episode(self):
        m_simple = requests_mock.Mocker()
        episode_id = self.episode_info["id"]
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
            IPodcastEpisodeInfo(episode).podcast.title)
        self.assertTrue(
            IPodcastEpisodeInfo(episode).is_published)

    def test_update_episode(self):
        episode_id = self.episode_info["id"]
        self.create_audio(self.episode_info)
        self.assertEqual(
            'Cat Jokes Pawdcast',
            self.repository['podcasts']['2023-08'][episode_id].title)
        json = self.episode_info.copy()
        json['title'] = "Cat Jokes Pawdcast - Folge 2"
        m_simple = requests_mock.Mocker()
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{episode_id}",
            json=json)
        with m_simple:
            self.simplecast.update_episode(episode_id)
        episode = self.repository['podcasts']['2023-08'][episode_id]
        self.assertEqual('Cat Jokes Pawdcast - Folge 2', episode.title)

    def test_delete_episode(self):
        episode_id = self.episode_info["id"]
        self.create_audio(self.episode_info)
        self.assertTrue(
            IAudio.providedBy(
                self.repository['podcasts']['2023-08'][episode_id]))

        self.simplecast.delete_episode(episode_id)
        self.assertNotIn(episode_id, self.repository['podcasts']['2023-08'])

    @requests_mock.Mocker()
    def test_publish(self, m):
        self.create_audio(self.episode_info)
        content = self.repository['podcasts']['2023-08'][self.episode_info['id']]

        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert isinstance(workflow, PodcastWorkflow)
        assert workflow.can_publish() == zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
        assert not workflow.published

        m.get(f"https://testapi.simplecast.com/episodes/{self.episode_info['id']}",
              json=self.episode_info)
        self.simplecast.publish_episode(self.episode_info["id"])
        assert workflow.published

        # publish again, should have no effect
        self.simplecast.publish_episode(self.episode_info['id'])
        assert workflow.published

    def test_podcast_not_published_if_requirements_not_met_url(self):
        simplecast_resp = self.episode_info.copy()
        simplecast_resp['audio_file_url'] = None
        self._check_publishing_error(simplecast_resp, 'Audio URL is missing')

    def test_podcast_not_published_if_requirements_not_met_is_published(self):
        simplecast_resp = self.episode_info.copy()
        simplecast_resp['is_published'] = False
        self._check_publishing_error(simplecast_resp, 'Podcast Episode is not published by Provider')

    def _check_publishing_error(self, simplecast_resp, message):
        self.create_audio(simplecast_resp)
        content = self.repository['podcasts']['2023-08'][self.episode_info['id']]

        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert isinstance(workflow, PodcastWorkflow)
        assert workflow.can_publish() == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        assert not workflow.published
        assert message in workflow.error_messages[0]

        publish = zeit.cms.workflow.interfaces.IPublish(content)
        with pytest.raises(zeit.cms.workflow.interfaces.PublishingError,
                           match='Publish pre-conditions not satisifed.'):
            publish.publish(background=False)
        assert not workflow.published

    def test_missing_audio_type_uses_default_workflow(self):
        default_audio = zeit.content.audio.audio.Audio()
        default_audio.uniqueId = "http://xml.zeit.de/default"
        default_audio.url = "https://example.com/default.mp3"
        default_audio.external_id = "1234"

        workflow = zeit.cms.workflow.interfaces.IPublishInfo(default_audio)
        assert isinstance(workflow, AudioWorkflow)
        assert workflow.can_publish() == zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS

    def test_deleted_podcast_should_be_retracted(self):
        pass
