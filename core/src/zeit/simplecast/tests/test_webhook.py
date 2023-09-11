from unittest import mock

import json
import pytest
import requests_mock

import zeit.simplecast.testing
import zeit.simplecast.json.webhook


def episode_id():
    return 'b44b1838-4ff4-4c29-ba1c-9c4f4b863eac'


def episode_create():
    return {
        "sent_at": "2023-08-28 13:32:11.967735Z",
        "data": {
            "message": (
                "A new episode has been created. The new episode id is: "
                "`b44b1838-4ff4-4c29-ba1c-9c4f4b863eac`"),
            "href": (
                "localhost/testapi/episodes/"
                "b44b1838-4ff4-4c29-ba1c-9c4f4b863eac"),
            "event": "episode_created",
            "episode_id": episode_id()}}


def episode_update():
    return {
        "sent_at": "2023-08-28 13:32:12.553408Z",
        "data": {
            "message": (
                "An episode has been updated. The episode id is: "
                "`b44b1838-4ff4-4c29-ba1c-9c4f4b863eac`"),
            "href": (
                "localhost/testapi/episodes/"
                "b44b1838-4ff4-4c29-ba1c-9c4f4b863eac"),
            "event": "episode_updated",
            "episode_id": episode_id()}}


def episode_delete():
    return {
        'data': {
            'event': 'episode_deleted',
            'episode_id': episode_id()}}


def episode_url():
    return f'https://testapi.simplecast.com/episodes/{episode_id()}'


class TestWebHook(zeit.simplecast.testing.BrowserTestCase):

    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def test_webhook_environment(self):
        notification = zeit.simplecast.json.webhook.Notification()
        self.assertEqual(notification.environment, "testing")

    def test_body_result(self):
        self.caplog.clear()

        mocker = requests_mock.Mocker()
        mocker.get(episode_url(), json=self.episode_info)

        with mocker:
            browser = self.browser
            browser.post('http://localhost/@@simplecast_webhook',
                         json.dumps(episode_create()),
                         'application/x-javascript')

        self.assertGreater(len(self.caplog.messages), 0)

    def test_create_episode(self):
        with mock.patch(
                'zeit.simplecast.connection.Simplecast.create_episode') as create:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(episode_create()),
                'application/x-javascript')
            create.assert_called_with(episode_id())

    def test_update_episode(self):
        with mock.patch(
                'zeit.simplecast.connection.Simplecast.update_episode') as update:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(episode_update()),
                'application/x-javascript')
            update.assert_called_with(episode_id())

    def test_delete_episode(self):
        with mock.patch(
                'zeit.simplecast.connection.Simplecast.delete_episode') as delete:
            self.browser.post(
                'http://localhost/@@simplecast_webhook',
                json.dumps(episode_delete()),
                'application/x-javascript')
            delete.assert_called_with(episode_id())
