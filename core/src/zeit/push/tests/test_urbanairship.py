from datetime import datetime
from zeit.push.interfaces import PARSE_NEWS_CHANNEL
import json
import mock
import os
import pytz
import unittest
import urbanairship.push.core
import zeit.push.interfaces
import zeit.push.testing
import zeit.push.urbanairship
import zope.app.appsetup.product


def send(self):
    """Mock that sends to /validate/.

    We cannot mock the URL only, since the logger in the original `send`
    expects more data to be returned by the response.

    """
    body = json.dumps(self.payload)
    response = self._airship._request(
        method='POST',
        body=body,
        url='https://go.urbanairship.com/api/push/validate/',
        content_type='application/json',
        version=3
    )
    return urbanairship.push.core.PushResponse(response)


class PushTest(unittest.TestCase):

    level = 2
    layer = zeit.push.testing.ZCML_LAYER

    def setUp(self):
        super(PushTest, self).setUp()
        self.android_application_key = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_ANDROID_APPLICATION_KEY']
        self.android_master_secret = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_ANDROID_MASTER_SECRET']
        self.ios_application_key = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_IOS_APPLICATION_KEY']
        self.ios_master_secret = os.environ[
            'ZEIT_PUSH_URBANAIRSHIP_IOS_MASTER_SECRET']

    def test_push_works(self):
        api = zeit.push.urbanairship.Connection(
            self.android_application_key, self.android_master_secret,
            self.ios_application_key, self.ios_master_secret, 1)
        with mock.patch('urbanairship.push.core.Push.send', send):
            with mock.patch('urbanairship.push.core.PushResponse') as push:
                api.send('Push', 'http://example.com',
                         channels=PARSE_NEWS_CHANNEL)
                self.assertEqual(200, push.call_args[0][0].status_code)

    def test_invalid_credentials_should_raise(self):
        api = zeit.push.urbanairship.Connection(
            'invalid', 'invalid', 'invalid', 'invalid', 1)
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            api.send('Being pushy.', 'http://example.com',
                     channels=PARSE_NEWS_CHANNEL)

    def test_server_error_should_raise(self):
        response = mock.Mock()
        response.status_code = 500
        response.headers = {}
        response.content = ''
        response.json.return_value = {}
        api = zeit.push.urbanairship.Connection(
            self.android_application_key, self.android_master_secret,
            self.ios_application_key, self.ios_master_secret, 1)
        with mock.patch('requests.sessions.Session.request') as request:
            request.return_value = response
            with self.assertRaises(zeit.push.interfaces.TechnicalError):
                api.send('Being pushy.', 'http://example.com',
                         channels=PARSE_NEWS_CHANNEL)


class ConnectionTest(zeit.push.testing.TestCase):

    def connection(self, expire_interval=1):
        return zeit.push.urbanairship.Connection(
            'any', 'any', 'any', 'any', expire_interval)

    def test_pushes_to_android_and_ios(self):
        api = self.connection()
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels=PARSE_NEWS_CHANNEL)
            self.assertEqual(
                ['android'], push.call_args_list[0][0][0].device_types)
            self.assertEqual(
                ['ios'], push.call_args_list[1][0][0].device_types)

    def test_audience_tag_depends_on_channel(self):
        api = self.connection()
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels=PARSE_NEWS_CHANNEL)
            self.assertEqual(
                {'or': [{'tag': 'News'}], 'group': 'subscriptions'},
                push.call_args_list[0][0][0].audience)
            self.assertEqual(
                {'or': [{'tag': 'News'}], 'group': 'subscriptions'},
                push.call_args_list[1][0][0].audience)

    def test_raises_if_no_channel_given(self):
        api = self.connection()
        with self.assertRaises(ValueError):
            api.send('Being pushy.', 'http://example.com')

    def test_raises_if_channel_not_in_product_config(self):
        api = self.connection()
        with self.assertRaises(ValueError):
            api.send('foo', 'any', channels='i-am-not-in-product-config')

    def test_sets_expiration_time_in_payload(self):
        api = self.connection(expire_interval=3600)
        with mock.patch('zeit.push.mobile.datetime') as mock_datetime:
            mock_datetime.now.return_value = (
                datetime(2014, 07, 1, 10, 15, 7, 38, tzinfo=pytz.UTC))
            with mock.patch.object(api, 'push') as push:
                api.send('foo', 'any', channels=PARSE_NEWS_CHANNEL)
                self.assertEqual(
                    '2014-07-01T11:15:07',
                    push.call_args_list[0][0][0].options['expiry'])
                self.assertEqual(
                    '2014-07-01T11:15:07',
                    push.call_args_list[1][0][0].options['expiry'])

    def test_enriches_payload_with_tag_to_categorize_notification(self):
        api = self.connection()
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels=PARSE_NEWS_CHANNEL)
            android = push.call_args_list[0][0][0].notification['android']
            self.assertEqual('News', android['extra']['tag'])
            ios = push.call_args_list[1][0][0].notification['ios']
            self.assertEqual('News', ios['extra']['tag'])
