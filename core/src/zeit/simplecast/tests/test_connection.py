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
import zeit.simplecast.connection
import zeit.simplecast.interfaces
import zeit.simplecast.testing
import zeit.workflow.asset


class TestSimplecast(zeit.simplecast.testing.FunctionalTestCase):
    def create_audio(self, json):
        with mock.patch.object(self.simplecast, 'fetch_episode') as request:
            request.return_value = json
            self.simplecast.synchronize_episode(json['id'])
        self.repository.connector.search_result = [
            (f'http://xml.zeit.de/podcasts/2023-08/{json["id"]}')
        ]

    def setUp(self):
        super().setUp()
        self.simplecast = zeit.simplecast.connection.Simplecast()
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
                text='an error occurred',
            )
            self.simplecast.fetch_episode(episode_id)
        args, _ = self.trace_mock.call_args_list[0]
        self.assertEqual(500, args[1])
        self.assertEqual('an error occurred', args[2])

    @requests_mock.Mocker()
    def test_simplecast_request_timeout_exceptions_are_handled(self, m):
        episode_id = '1234'
        with self.assertRaises(requests.exceptions.Timeout):
            m.get(
                f'https://testapi.simplecast.com/episodes/{episode_id}',
                exc=requests.exceptions.ConnectTimeout,
            )
            self.simplecast.fetch_episode(episode_id)
        args, _ = self.trace_mock.call_args_list[0]
        self.assertEqual(599, args[1])
        self.assertEqual('', args[2])

    @requests_mock.Mocker()
    def test_simplecast_request_json_errors_are_handled(self, m):
        episode_id = '1234'
        with self.assertRaises(requests.exceptions.JSONDecodeError):
            m.get(f'https://testapi.simplecast.com/episodes/{episode_id}', text='no json')
            self.simplecast.fetch_episode(episode_id)
        args, _ = self.trace_mock.call_args_list[0]
        self.assertEqual(200, args[1])
        self.assertEqual(
            'Invalid Json Expecting value: ' 'line 1 column 1 (char 0): no json', args[2]
        )

    def test_simplecast_yields_episode_info(self):
        m_simple = requests_mock.Mocker()
        episode_id = self.episode_info['id']
        m_simple.get(
            f'https://testapi.simplecast.com/episodes/{episode_id}', json=self.episode_info
        )
        with m_simple:
            result = self.simplecast.fetch_episode(episode_id)
            self.assertEqual(result, self.episode_info)

    def test_simplecast_gets_podcast_folder(self):
        container = self.simplecast.folder(self.episode_info['created_at'])
        self.assertEqual(container, self.repository['podcasts']['2023-08'])

    def test_update_published_or_unpublished_episodes_should_publish_or_retract_audio_object(self):
        boolsets = [
            (True, True, True, False),
            (True, False, False, True),
            (False, True, True, False),
            (False, False, False, False),
        ]
        for initial_state, updated_state, publish_expected, retract_expected in boolsets:
            self.episode_info['is_published'] = initial_state
            episode_id = self.episode_info['id']
            self.create_audio(self.episode_info)
            audio_object = self.repository['podcasts']['2023-08'][episode_id]
            assert (
                zeit.cms.workflow.interfaces.IPublishInfo(audio_object).published == initial_state
            )
            self.episode_info['is_published'] = updated_state
            m_simple = requests_mock.Mocker()
            m_simple.get(
                f'https://testapi.simplecast.com/episodes/{episode_id}', json=self.episode_info
            )
            retract = mock.Mock()
            publish = mock.Mock()
            zope.component.getGlobalSiteManager().registerHandler(
                retract, (zeit.cms.workflow.interfaces.IRetractedEvent,)
            )
            zope.component.getGlobalSiteManager().registerHandler(
                publish, (zeit.cms.workflow.interfaces.IPublishedEvent,)
            )
            with m_simple:
                self.simplecast.synchronize_episode(episode_id)
            self.assertEqual(publish_expected, publish.called)
            self.assertEqual(retract_expected, retract.called)

    def test_update_episode(self):
        episode_id = self.episode_info['id']
        self.create_audio(self.episode_info)
        self.assertEqual(
            'Cat Jokes Pawdcast', self.repository['podcasts']['2023-08'][episode_id].title
        )
        json = self.episode_info.copy()
        json['title'] = 'Cat Jokes Pawdcast - Folge 2'
        m_simple = requests_mock.Mocker()
        m_simple.get(f'https://testapi.simplecast.com/episodes/{episode_id}', json=json)
        with m_simple:
            self.simplecast.synchronize_episode(episode_id)
        episode = self.repository['podcasts']['2023-08'][episode_id]
        self.assertEqual('Cat Jokes Pawdcast - Folge 2', episode.title)
        self.assertEqual(
            pendulum.datetime(2020, 7, 13, 14, 21, 39, tz='UTC'),
            ISemanticChange(episode).last_semantic_change,
        )

    def test_should_skip_update_for_already_locked_object(self):
        episode_id = self.episode_info['id']
        self.create_audio(self.episode_info)
        json = self.episode_info.copy()
        json['title'] = 'Cat Jokes Pawdcast - Folge 2'
        m_simple = requests_mock.Mocker()
        m_simple.get(f'https://testapi.simplecast.com/episodes/{episode_id}', json=json)

        episode = self.repository['podcasts']['2023-08'][episode_id]
        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.producer'):
            zeit.cms.checkout.interfaces.ICheckoutManager(episode).checkout()
        zeit.cms.testing.create_interaction('zope.user')

        with m_simple:
            self.simplecast.synchronize_episode(episode_id)
        episode = self.repository['podcasts']['2023-08'][episode_id]
        self.assertNotEqual(json['title'], episode.title)

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

        m.get(
            f"https://testapi.simplecast.com/episodes/{self.episode_info['id']}",
            json=simplecast_resp,
        )

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
        self._check_publishing_error(
            simplecast_resp, 'Podcast Episode is not published by Provider'
        )

    def _check_publishing_error(self, simplecast_resp, message):
        self.create_audio(simplecast_resp)
        content = self.repository['podcasts']['2023-08'][self.episode_info['id']]

        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert isinstance(workflow, PodcastWorkflow)
        assert workflow.can_publish() == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        assert not workflow.published
        assert message in workflow.error_messages[0]

        publish = zeit.cms.workflow.interfaces.IPublish(content)
        with pytest.raises(
            zeit.cms.workflow.interfaces.PublishingError,
            match='Publish pre-conditions not satisifed.',
        ):
            publish.publish(background=False)
        assert not workflow.published

    def test_missing_audio_type_uses_default_workflow(self):
        default_audio = zeit.content.audio.audio.Audio()
        default_audio.uniqueId = 'http://xml.zeit.de/default'
        default_audio.url = 'https://example.com/default.mp3'
        default_audio.external_id = '1234'

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

        m.get(
            f"https://testapi.simplecast.com/episodes/{self.episode_info['id']}",
            json=self.episode_info,
        )
        self.simplecast.synchronize_episode(self.episode_info['id'])
        assert (
            IPodcastEpisodeInfo(content).is_published is False
        ), 'retract should set is_published to False'

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
            retract, (zeit.cms.workflow.interfaces.IRetractedEvent,)
        )

        m_simple = requests_mock.Mocker()
        m_simple.get(
            f"https://testapi.simplecast.com/episodes/{self.episode_info['id']}", status_code=404
        )
        with m_simple:
            self.simplecast.synchronize_episode(self.episode_info['id'])
        self.assertEqual(True, retract.called)
        assert not workflow.published

    def test_no_episode_and_no_audio_in_vivi(self):
        episode_id = self.episode_info['id']
        json = self.episode_info.copy()
        json['title'] = 'Cat Jokes Pawdcast - Folge 2'
        m_simple = requests_mock.Mocker()
        m_simple.get(f'https://testapi.simplecast.com/episodes/{episode_id}', status_code=404)
        with m_simple:
            self.simplecast.synchronize_episode(episode_id)
        retract = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            retract, (zeit.cms.workflow.interfaces.IRetractedEvent,)
        )
        self.assertFalse(retract.called)


class TestSimplecastExternalAPI:
    def test_simplecast_get_episodes_response(self):
        # DIE ZEIT: Hinter der Geschichte - Per WhatsApp in die Antarktis
        response = requests.get(
            'https://api.simplecast.com/episodes/338dfff7-e878-4312-b519-40387be19a54'
        )
        assert response.status_code == 200
        body = response.json()
        expected_items = {
            'title': 'Per WhatsApp in die Antarktis',
            'audio_file_url': 'https://zeitonline.simplecastaudio.com/f6642392-cca5-412a-9ff0-a5b9ba1f1717/episodes/338dfff7-e878-4312-b519-40387be19a54/audio/128/default.mp3?awCollectionId=f6642392-cca5-412a-9ff0-a5b9ba1f1717&awEpisodeId=338dfff7-e878-4312-b519-40387be19a54',
            'duration': 1278,
            'id': '338dfff7-e878-4312-b519-40387be19a54',
            'number': 253,
            'description': 'Die Polarforscherin Stefanie Arndt befindet sich gerade für 100 Tage am Südpol – und beantwortet dort fast täglich Kinderfragen. Katrin Hörnlein, die verantwortliche Redakteurin im Ressort »Junge Leser« der ZEIT, sammelt diese Fragen und schickt sie in die Antarktis. Dort antwortet Stefanie Arndt per WhatsApp-Sprachnachricht. So entsteht eine Art Forschungstagebuch in der ZEIT und dem Magazin ZEIT Leo, an dem die jungen Leserinnen und Leser mitrecherchieren. Im Podcast »Hinter der Geschichte« berichtet Katrin Hörnlein von diesem Projekt. Stefanie Arndt meldet sich zwischendurch per Sprachnachricht und erzählt von der endlosen Weite der Eislandschaft, von Pinguinen und davon, wie dick ihr Schlafanzug ist.',  # noqa: E501
            'long_description': '\nDie Polarforscherin Stefanie Arndt befindet sich gerade für 100 Tage am Südpol – und beantwortet dort fast täglich Kinderfragen. Katrin Hörnlein, die verantwortliche Redakteurin im Ressort »Junge Leser« der ZEIT, sammelt diese Fragen und schickt sie in die Antarktis. Dort antwortet Stefanie Arndt per WhatsApp-Sprachnachricht. So entsteht eine Art Forschungstagebuch in der ZEIT und dem Magazin ZEIT Leo, an dem die jungen Leserinnen und Leser mitrecherchieren. Im Podcast »Hinter der Geschichte« berichtet Katrin Hörnlein von diesem Projekt. Stefanie Arndt meldet sich zwischendurch per Sprachnachricht und erzählt von der endlosen Weite der Eislandschaft, von Pinguinen und davon, wie dick ihr Schlafanzug ist.',  # noqa: E501
            'is_published': True,
            'updated_at': '2023-10-26T09:08:32+02:00',
        }
        for key, value in expected_items.items():
            assert body[key] == value, f'Simplecast Response for {key} is not what we expected!'
        assert body['podcast']['id'] == 'f6642392-cca5-412a-9ff0-a5b9ba1f1717'
