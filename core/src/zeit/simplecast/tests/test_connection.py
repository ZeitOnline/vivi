from unittest import mock

import pendulum
import requests
import requests_mock
import transaction
import zope.component

from zeit.cms.content.interfaces import ISemanticChange
from zeit.content.audio.interfaces import IPodcastEpisodeInfo
import zeit.cms.repository.folder
import zeit.cms.workflow.interfaces
import zeit.content.audio.audio
import zeit.simplecast.connection
import zeit.simplecast.interfaces
import zeit.simplecast.testing
import zeit.workflow.asset
import zeit.workflow.publish_3rdparty


class TestSimplecastAPI(zeit.simplecast.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.simplecast = zeit.simplecast.connection.Simplecast()
        self.trace_patch = mock.patch('zeit.cms.tracing.record_span')
        self.trace_mock = self.trace_patch.start()

    def tearDown(self):
        self.trace_patch.stop()
        super().tearDown()

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
        self.assertEqual('Invalid Json Expecting value: line 1 column 1 (char 0): no json', args[2])

    @requests_mock.Mocker()
    def test_simplecast_too_many_requests_raises(self, m):
        episode_id = '1234'
        m.get(
            f'https://testapi.simplecast.com/episodes/{episode_id}',
            status_code=429,
        )
        with self.assertRaises(zeit.simplecast.interfaces.TechnicalError):
            self.simplecast.fetch_episode(episode_id)
        args, _ = self.trace_mock.call_args_list[0]
        self.assertEqual(429, args[1])

    def test_simplecast_yields_episode_info(self):
        m_simple = requests_mock.Mocker()
        episode_id = self.episode_info['id']
        m_simple.get(
            f'https://testapi.simplecast.com/episodes/{episode_id}', json=self.episode_info
        )
        with m_simple:
            result = self.simplecast.fetch_episode(episode_id)
            self.assertEqual(result, self.episode_info)

    @requests_mock.Mocker()
    def test_fetch_episode_translates_notfound_to_none(self, m):
        episode_id = self.episode_info['id']
        m.get(f'https://testapi.simplecast.com/episodes/{episode_id}', status_code=404)
        self.assertEqual(None, self.simplecast.fetch_episode(episode_id))


class TestImportAudio(zeit.simplecast.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.simplecast = zeit.simplecast.connection.Simplecast()
        mock.patch.object(self.simplecast, 'fetch_episode', return_value=self.episode_info).start()

    def synchronize(self):
        self.simplecast.synchronize_episode(self.episode_info['id'])
        transaction.commit()

    def test_simplecast_gets_podcast_folder(self):
        container = self.simplecast._find_or_create_folder(self.episode_info['created_at'])
        self.assertEqual(container, self.repository['podcasts']['2023-08'])

    def _test_publish_retract_behavior(
        self, initial_state, updated_state, publish_expected, retract_expected
    ):
        self.episode_info['is_published'] = initial_state
        self.synchronize()
        audio_object = self.repository['podcasts']['2023-08'][self.episode_id]
        assert zeit.cms.workflow.interfaces.IPublishInfo(audio_object).published == initial_state
        self.episode_info['is_published'] = updated_state
        retract = mock.Mock()
        publish = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            retract, (zeit.cms.workflow.interfaces.IRetractedEvent,)
        )
        zope.component.getGlobalSiteManager().registerHandler(
            publish, (zeit.cms.workflow.interfaces.IPublishedEvent,)
        )
        self.synchronize()
        self.assertEqual(publish_expected, publish.called)
        self.assertEqual(retract_expected, retract.called)

    def test_update_published_to_published_should_publish(self):
        self._test_publish_retract_behavior(
            initial_state=True,
            updated_state=True,
            publish_expected=True,
            retract_expected=False,
        )

    def test_update_published_to_unpublished_should_retract(self):
        self._test_publish_retract_behavior(
            initial_state=True,
            updated_state=False,
            publish_expected=False,
            retract_expected=True,
        )

    def test_update_unpublished_to_published_should_publish(self):
        self._test_publish_retract_behavior(
            initial_state=False,
            updated_state=True,
            publish_expected=True,
            retract_expected=False,
        )

    def test_update_unpublished_to_unpublished_should_do_nothing(self):
        self._test_publish_retract_behavior(
            initial_state=False,
            updated_state=False,
            publish_expected=False,
            retract_expected=False,
        )

    def test_update_episode(self):
        self.synchronize()
        self.assertEqual(
            'Cat Jokes Pawdcast', self.repository['podcasts']['2023-08'][self.episode_id].title
        )
        self.episode_info['title'] = 'Cat Jokes Pawdcast - Folge 2'
        self.synchronize()
        episode = self.repository['podcasts']['2023-08'][self.episode_id]
        self.assertEqual('Cat Jokes Pawdcast - Folge 2', episode.title)
        self.assertEqual(
            pendulum.datetime(2020, 7, 13, 14, 21, 39, tz='UTC'),
            ISemanticChange(episode).last_semantic_change,
        )

    def test_should_skip_update_for_already_locked_object(self):
        self.synchronize()
        self.episode_info['title'] = 'Cat Jokes Pawdcast - Folge 2'
        episode = self.repository['podcasts']['2023-08'][self.episode_id]
        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.producer'):
            zeit.cms.checkout.interfaces.ICheckoutManager(episode).checkout()
        zeit.cms.testing.create_interaction('zope.user')

        self.synchronize()
        episode = self.repository['podcasts']['2023-08'][self.episode_id]
        self.assertNotEqual(self.episode_info['title'], episode.title)

    def test_publish(self):
        self.episode_info['is_published'] = True
        self.synchronize()
        content = self.repository['podcasts']['2023-08'][self.episode_id]

        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert workflow.can_publish() == zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
        assert workflow.published

        # publish again, should have no effect
        self.synchronize()
        assert workflow.published

    def test_retract(self):
        self.episode_info['is_published'] = True
        self.synchronize()
        content = self.repository['podcasts']['2023-08'][self.episode_id]
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert workflow.published

        self.episode_info['is_published'] = False
        self.synchronize()
        assert IPodcastEpisodeInfo(content).is_published is False, (
            'retract should set is_published to False'
        )
        assert not workflow.published

    def test_deleted_podcast_should_be_retracted(self):
        self.episode_info['is_published'] = True
        self.synchronize()
        content = self.repository['podcasts']['2023-08'][self.episode_id]
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        assert workflow.published

        retract = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            retract, (zeit.cms.workflow.interfaces.IRetractedEvent,)
        )

        with mock.patch.object(self.simplecast, 'fetch_episode', return_value=None):
            self.synchronize()
        self.assertEqual(True, retract.called)
        assert not workflow.published

    def test_no_episode_and_no_audio_in_vivi(self):
        self.episode_info['title'] = 'Cat Jokes Pawdcast - Folge 2'
        self.synchronize()
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
