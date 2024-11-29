from unittest import mock
import json

import zeit.brightcove.convert
import zeit.brightcove.testing
import zeit.cms.testing


class NotificationTest(zeit.brightcove.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.patch = mock.patch.object(zeit.brightcove.update.import_video_async, '__call__')
        self.import_video = self.patch.start()
        # Webhook view is available without authentication
        self.browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

    def test_runs_import_as_system_user(self):
        self.browser.post(
            'http://localhost/@@update_video',
            json.dumps({'event': 'video-change', 'video': 'myvid'}),
            'application/json',
        )
        self.assertEqual('myvid', self.import_video.call_args[0][0])
        self.assertEqual('zope.user', self.import_video.call_args[1]['_principal_id_'])

    def test_ignores_event_if_origin_is_ourselves(self):
        self.browser.post(
            'http://localhost/@@update_video',
            json.dumps(
                {
                    'event': 'video-change',
                    'video': 'myvid',
                    'updated_by': {'type': 'api_key', 'email': 'vivi@example.com'},
                }
            ),
            'application/json',
        )
        self.assertFalse(self.import_video.called)
