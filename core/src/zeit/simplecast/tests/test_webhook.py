from unittest import mock

import json
import pytest
import requests_mock

import zeit.simplecast.testing
import zeit.simplecast.json.webhook


def episode_id():
    return 'b44b1838-4ff4-4c29-ba1c-9c4f4b863eac'


def webhook_event(event_type):
    event = event_type.split('_')[1]
    body = {
        "sent_at": "2023-08-28 13:32:11.967735Z",
        "data": {
            "message": f"An episode has been {event}. The episode id is: `{episode_id()}`",
            "href": (
                f"localhost/testapi/episodes/{episode_id()}"),
            "event": event_type,
            "episode_id": episode_id()
        }
    }
    if event_type == 'episode_deleted':
        body['data'].pop('message')
        body['data'].pop('href')

    return body


def episode_url():
    return f'https://testapi.simplecast.com/episodes/{episode_id()}'


class TestWebHook(zeit.simplecast.testing.BrowserTestCase):

    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def test_body_result(self):
        self.caplog.clear()

        mocker = requests_mock.Mocker()
        mocker.get(episode_url(), json=self.episode_info)

        with mocker:
            browser = self.browser
            browser.post('http://localhost/@@simplecast_webhook',
                         json.dumps(webhook_event('episode_created')),
                         'application/x-javascript')

        self.assertGreater(len(self.caplog.messages), 0)

    def test_create_episode(self):
        event = webhook_event('episode_created')
        with mock.patch(
                'zeit.simplecast.connection.Simplecast.create_episode') as create:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(event),
                'application/x-javascript')
            create.assert_called_with(episode_id())

    def test_update_episode(self):
        event = webhook_event('episode_updated')
        with mock.patch(
                'zeit.simplecast.connection.Simplecast.update_episode') as update:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(event),
                'application/x-javascript')
            update.assert_called_with(episode_id())

    def test_delete_episode(self):
        event = webhook_event('episode_deleted')
        with mock.patch(
                'zeit.simplecast.connection.Simplecast.delete_episode') as delete:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(event),
                'application/x-javascript')
            delete.assert_called_with(episode_id())

    def test_publish_episode(self):
        event = webhook_event('episode_published')
        with mock.patch(
                'zeit.simplecast.connection.Simplecast.publish_episode') as publish:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(event),
                'application/x-javascript')
            publish.assert_called_with(episode_id())

    def test_unpublish_episode(self):
        event = webhook_event('episode_unpublished')
        with mock.patch(
                'zeit.simplecast.connection.Simplecast.retract_episode') as retract:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(event),
                'application/x-javascript')
            retract.assert_called_with(episode_id())

    def test_webhook_body_is_traced(self):
        # only exemplary for `episode_updated`
        event = webhook_event('episode_updated')
        with (mock.patch(
                'opentelemetry.trace.get_current_span') as cs,
                mock.patch('zeit.simplecast.connection.Simplecast.update_episode')):
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(event),
                'application/x-javascript')
            self.assertEllipsis("...set_attributes({'http.body': {'message': 'An episode...set_attribute('enduser.id'...", str(cs.mock_calls)) # noqa
