import pytest
import json
import requests_mock
import zope.component

import zeit.content.audio.audio
import zeit.simplecast.testing
import zeit.simplecast.json.webhook
import zeit.cms.repository.folder


def episode_id():
    return 'b44b1838-4ff4-4c29-ba1c-9c4f4b863eac'


def episode_create():
    return {
        "sent_at": "2023-08-28 13:32:11.967735Z",
        "data": {
            "message": "A new episode has been created. The new episode id is: `b44b1838-4ff4-4c29-ba1c-9c4f4b863eac`",
            "href": "localhost/testapi/episodes/b44b1838-4ff4-4c29-ba1c-9c4f4b863eac",
            "event": "episode_created",
            "episode_id": episode_id()}}


def episode_update():
    return {
        "sent_at": "2023-08-28 13:32:12.553408Z",
        "data": {
            "message": "An episode has been updated. The episode id is: `b44b1838-4ff4-4c29-ba1c-9c4f4b863eac`",
            "href": "localhost/testapi/episodes/b44b1838-4ff4-4c29-ba1c-9c4f4b863eac",
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
    def test_webhook_environment(self):
        notification = zeit.simplecast.json.webhook.Notification()
        self.assertEqual(notification.environment, "testing")

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
                         json.dumps(episode_create()),
                         'application/x-javascript')

        self.assertGreater(len(self.caplog.messages), 0)

    def test_create_episode(self):
        mocker = requests_mock.Mocker()
        mocker.get(episode_url(), json=self.episode_info)

        with mocker:
            browser = self.browser
            browser.post('http://localhost/@@simplecast_webhook',
                         json.dumps(episode_create()),
                         'application/x-javascript')

        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        container = simplecast.folder(self.episode_info['created_at'])
        episode = container[episode_id()]
        self.assertEqual(episode.title, 'Episode 42')
        self.assertEqual(episode.episode_id, episode_id())
        self.assertEqual(episode.url, self.episode_info['audio_file_url'])

    def test_update_episode(self):
        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        container = simplecast.folder(self.episode_info['created_at'])
        zeit.content.audio.audio.add_audio(container, self.episode_info)

        info = self.episode_info
        info['title'] = 'New title'

        mocker = requests_mock.Mocker()
        mocker.get(episode_url(), json=info)

        with mocker:
            browser = self.browser
            browser.post('http://localhost/@@simplecast_webhook',
                         json.dumps(episode_update()),
                         'application/x-javascript')

        episode = container[episode_id()]
        self.assertEqual(episode.title, 'New title')

    def test_delete_episode(self):
        simplecast = zope.component.getUtility(
            zeit.simplecast.interfaces.ISimplecast)
        container = simplecast.folder(self.episode_info['created_at'])
        zeit.content.audio.audio.add_audio(container, self.episode_info)

        browser = self.browser
        browser.post('http://localhost/@@simplecast_webhook',
                     json.dumps(episode_delete()),
                     'application/x-javascript')

        self.assertNotIn(episode_id(), container)
