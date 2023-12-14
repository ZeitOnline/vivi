import json
import pytest
import requests_mock
import zope.component

import zeit.simplecast.testing
import zeit.simplecast.json.webhook


def episode_id():
    return 'b44b1838-4ff4-4c29-ba1c-9c4f4b863eac'


def webhook_event(event_type):
    event = event_type.split('_')[1]
    body = {
        'sent_at': '2023-08-28 13:32:11.967735Z',
        'data': {
            'message': f'An episode has been {event}. The episode id is: `{episode_id()}`',
            'href': (f'localhost/testapi/episodes/{episode_id()}'),
            'event': event_type,
            'episode_id': episode_id(),
        },
    }
    if event_type == 'episode_deleted':
        body['data'].pop('message')
        body['data'].pop('href')

    return body


def episode_url():
    return f'https://testapi.simplecast.com/episodes/{episode_id()}'


class TestWebHook(zeit.simplecast.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.simplecast = zope.component.getUtility(zeit.simplecast.interfaces.ISimplecast)

    def tearDown(self):
        self.simplecast.reset_mock()

    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def test_body_result(self):
        self.caplog.clear()

        mocker = requests_mock.Mocker()
        mocker.get(episode_url(), json=self.episode_info)

        with mocker:
            browser = self.browser
            browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(webhook_event('episode_created')),
                'application/x-javascript',
            )

        self.assertGreater(len(self.caplog.messages), 0)

    def test_broken_event(self):
        self.browser.post(
            'http://localhost/@@simplecast_webhook',
            json.dumps({'data': {}}),
            'application/x-javascript',
        )
        self.simplecast.fetch_episode_audio.assert_not_called()
        self.simplecast.synchronize_episode.assert_not_called()

    def test_transcode_finished(self):
        episode_audio_id = '9185df81-b5fc-4686-86e4-2a7bb38a33f9'
        self.simplecast.fetch_episode_audio.return_value = {
            'episode_id': episode_id(),
        }
        event = {
            'sent_at': '2023-12-12 10:22:06.093797Z',
            'data': {
                'message': 'The audio for an episode has finished transcoding. '
                f'The episode audio id is: `{episode_audio_id}`',
                'href': f'https://api.simplecast.com/episodes/audio/{episode_audio_id}',
                'event': 'transcode_finished',
                'episode_audio_id': f'{episode_audio_id}',
            },
        }
        self.browser.post(
            'http://localhost/@@simplecast_webhook',
            json.dumps(event),
            'application/x-javascript',
        )
        self.simplecast.fetch_episode_audio.assert_called_with(episode_audio_id)
        self.simplecast.synchronize_episode.assert_called_with(episode_id())

    def test_create_episode(self):
        event = webhook_event('episode_created')
        self.browser.post(
            'http://localhost/@@simplecast_webhook',
            json.dumps(event),
            'application/x-javascript',
        )
        self.simplecast.synchronize_episode.assert_called_with(episode_id())

    def test_update_episode(self):
        event = webhook_event('episode_updated')
        self.browser.post(
            'http://localhost/@@simplecast_webhook',
            json.dumps(event),
            'application/x-javascript',
        )
        self.simplecast.synchronize_episode.assert_called_with(episode_id())

    def test_delete_episode(self):
        event = webhook_event('episode_deleted')
        self.browser.post(
            'http://localhost/@@simplecast_webhook',
            json.dumps(event),
            'application/x-javascript',
        )
        self.simplecast.synchronize_episode.assert_called_with(episode_id())

    def test_publish_episode(self):
        event = webhook_event('episode_published')
        self.browser.post(
            'http://localhost/@@simplecast_webhook',
            json.dumps(event),
            'application/x-javascript',
        )
        self.simplecast.synchronize_episode.assert_called_with(episode_id())

    def test_unpublish_episode(self):
        event = webhook_event('episode_unpublished')
        self.browser.post(
            'http://localhost/@@simplecast_webhook',
            json.dumps(event),
            'application/x-javascript',
        )
        self.simplecast.synchronize_episode.assert_called_with(episode_id())

    def test_webhook_body_is_traced(self):
        # only exemplary for `episode_updated`
        event = webhook_event('episode_updated')
        with zeit.cms.testing.captrace() as trace:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(event),
                'application/x-javascript',
            )
            span = trace['POST /@@simplecast_webhook']
            self.assertEqual(json.dumps(event), span.attributes['http.body'])
