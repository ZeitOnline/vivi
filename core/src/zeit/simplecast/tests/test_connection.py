from unittest import mock

import pendulum
import pytest
import requests_mock
import requests
import zope.component

from zeit.cms.content.interfaces import ISemanticChange
from zeit.content.audio.interfaces import IPodcastEpisodeInfo
from zeit.content.audio.workflow import AudioWorkflow, PodcastWorkflow
import zeit.cms.repository.folder
import zeit.cms.workflow.interfaces
import zeit.content.audio.audio
import zeit.simplecast.interfaces
import zeit.simplecast.testing
import zeit.workflow.asset


class TestSimplecastAPI(zeit.simplecast.testing.FunctionalTestCase):

    def create_audio(self, json):
        with mock.patch.object(self.simplecast, '_fetch_episode') as request:
            request.return_value = json
            self.simplecast.synchronize_episode(json['id'])
        self.repository.connector.search_result = [(f'http://xml.zeit.de/podcasts/2023-08/{json["id"]}')]

    def setUp(self):
        super().setUp()
        self.simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        self.trace_patch = mock.patch('zeit.cms.tracing.record_span')
        self.trace_mock = self.trace_patch.start()

    def tearDown(self):
        super().tearDown()
        self.trace_patch.stop()

    @requests_mock.Mocker()
    def test_simplecast_request_exceptions_are_handled(self, m):
        episode_id = '1234'
        with self.assertRaises(requests.exceptions.RequestException):
            m.get(
                f'https://testapi.simplecast.com/episodes/{episode_id}',
                status_code=500,
                text='an error occurred')
            self.simplecast._fetch_episode(episode_id)
        args, _ = self.trace_mock.call_args_list[0]
        self.assertEqual(500, args[1])
        self.assertEqual('an error occurred', args[2])

    @requests_mock.Mocker()
    def test_simplecast_request_timeout_exceptions_are_handled(self, m):
        episode_id = '1234'
        with self.assertRaises(requests.exceptions.Timeout):
            m.get(
                f'https://testapi.simplecast.com/episodes/{episode_id}',
                exc=requests.exceptions.ConnectTimeout)
            self.simplecast._fetch_episode(episode_id)
        args, _ = self.trace_mock.call_args_list[0]
        self.assertEqual(599, args[1])
        self.assertEqual('', args[2])

    @requests_mock.Mocker()
    def test_simplecast_request_json_errors_are_handled(self, m):
        episode_id = '1234'
        with self.assertRaises(requests.exceptions.JSONDecodeError):
            m.get(
                f'https://testapi.simplecast.com/episodes/{episode_id}',
                text="no json")
            self.simplecast._fetch_episode(episode_id)
        args, _ = self.trace_mock.call_args_list[0]
        self.assertEqual(200, args[1])
        self.assertEqual('Invalid Json Expecting value: '
                         'line 1 column 1 (char 0): no json', args[2])

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
            self.simplecast.synchronize_episode(episode_id)
        episode = self.repository['podcasts']['2023-08'][episode_id]
        self.assertEqual('Cat Jokes Pawdcast - Folge 2', episode.title)
        self.assertEqual(
            pendulum.datetime(2020, 7, 13, 14, 21, 39, tz='UTC'),
            ISemanticChange(episode).last_semantic_change)

    @requests_mock.Mocker()
    def test_publish(self, m):
        simplecast_resp = self.episode_info.copy()
        simplecast_resp['is_published'] = True
        self.create_audio(simplecast_resp)
        content = self.repository['podcasts']['2023-08'][self.episode_info['id']]

        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert isinstance(workflow, PodcastWorkflow)
        assert workflow.can_publish() == zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
        assert workflow.published

        m.get(f"https://testapi.simplecast.com/episodes/{self.episode_info['id']}",
              json=simplecast_resp)

        # publish again, should have no effect
        self.simplecast.synchronize_episode(self.episode_info['id'])
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

    @requests_mock.Mocker()
    def test_retract(self, m):
        simplecast_resp = self.episode_info.copy()
        simplecast_resp['is_published'] = True
        self.create_audio(simplecast_resp)
        content = self.repository['podcasts']['2023-08'][self.episode_info['id']]
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert workflow.published

        m.get(f"https://testapi.simplecast.com/episodes/{self.episode_info['id']}",
              json=self.episode_info)
        self.simplecast.synchronize_episode(self.episode_info["id"])
        assert IPodcastEpisodeInfo(content).is_published is False, 'retract should set is_published to False'

        assert not workflow.published

    @requests_mock.Mocker()
    def test_deleted_podcast_should_be_retracted(self, m):
        simplecast_resp = self.episode_info.copy()
        simplecast_resp['is_published'] = True
        self.create_audio(simplecast_resp)
        content = self.repository['podcasts']['2023-08'][self.episode_info['id']]
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert workflow.published

        retract = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            retract, (zeit.cms.workflow.interfaces.IRetractedEvent,))

        m_simple = requests_mock.Mocker()
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{self.episode_info['id']}",
            status_code=404)
        with m_simple:
            self.simplecast.synchronize_episode(self.episode_info["id"])
        self.assertEqual(True, retract.called)
        assert not workflow.published

    def test_no_episode_and_no_audio_in_vivi(self):
        episode_id = self.episode_info["id"]
        json = self.episode_info.copy()
        json['title'] = "Cat Jokes Pawdcast - Folge 2"
        m_simple = requests_mock.Mocker()
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{episode_id}",
            status_code=404)
        with m_simple:
            self.simplecast.synchronize_episode(episode_id)
        retract = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            retract, (zeit.cms.workflow.interfaces.IRetractedEvent,))
        self.assertFalse(retract.called)
