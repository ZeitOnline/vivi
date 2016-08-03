from datetime import datetime
from zeit.push.interfaces import PARSE_NEWS_CHANNEL
import mock
import os
import pytz
import unittest
import zeit.push.parse
import zeit.push.testing
import zope.app.appsetup.product


class PushTest(unittest.TestCase):

    level = 2
    layer = zeit.push.testing.ZCML_LAYER

    def setUp(self):
        super(PushTest, self).setUp()
        self.app_id = os.environ['ZEIT_PUSH_PARSE_APP_ID']
        self.api_key = os.environ['ZEIT_PUSH_PARSE_API_KEY']

    def test_push_works(self):
        # Parse offers no REST API to retrieve push messages,
        # so this is just a smoke test.
        api = zeit.push.parse.Connection(self.app_id, self.api_key, 1)
        api.send('Being pushy.', 'http://example.com', skip_ios=True)

    def test_push_works_with_channels(self):
        api = zeit.push.parse.Connection(
            self.app_id, self.api_key, 1)
        api.send('Being pushy.', 'http://example.com', channels=['News'],
                 skip_ios=True)

    def test_invalid_credentials_should_raise(self):
        api = zeit.push.parse.Connection('invalid', 'invalid', 1)
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            api.send('Being pushy.', 'http://example.com')

    def test_server_error_should_raise(self):
        response = mock.Mock()
        response.status_code = 500
        api = zeit.push.parse.Connection(self.app_id, self.api_key, 1)
        with mock.patch('requests.post') as post:
            post.return_value = response
            with self.assertRaises(zeit.push.interfaces.TechnicalError):
                api.send('Being pushy.', 'http://example.com')


class ConnectionTest(zeit.push.testing.TestCase):

    def test_pushes_to_android_and_ios(self):
        api = zeit.push.parse.Connection(None, None, 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any')
            self.assertEqual({
                'deviceType': 'android',
                'appVersion': {'$gte': '1.4'},
            }, push.call_args_list[0][0][0]['where'])
            self.assertEqual({
                'deviceType': 'ios',
                'appVersion': {'$gte': '20150914'},
            }, push.call_args_list[1][0][0]['where'])

    def test_channels_can_be_set_via_parameter(self):
        api = zeit.push.parse.Connection(None, None, 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels=PARSE_NEWS_CHANNEL)
            self.assertEqual(
                ['News'],
                push.call_args_list[0][0][0]['where']['channels']['$in'])
            self.assertEqual(
                ['News'],
                push.call_args_list[1][0][0]['where']['channels']['$in'])

    def test_no_channels_given_omits_channels_parameter(self):
        api = zeit.push.parse.Connection(None, None, 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any')
            self.assertNotIn('channels', push.call_args_list[0][0][0]['where'])
            self.assertNotIn('channels', push.call_args_list[1][0][0]['where'])

    def test_empty_product_config_omits_channels_parameter(self):
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push')
        product_config['foo'] = ''
        api = zeit.push.parse.Connection('any', 'any', 1)
        with mock.patch.object(api, 'push') as push:
            api.send('foo', 'any', channels='foo')
            self.assertNotIn('channels', push.call_args_list[0][0][0]['where'])
            self.assertNotIn('channels', push.call_args_list[1][0][0]['where'])

    def test_sets_expiration_time_in_payload(self):
        api = zeit.push.parse.Connection('any', 'any', 3600)
        with mock.patch('zeit.push.mobile.datetime') as mock_datetime:
            mock_datetime.now.return_value = (
                datetime(2014, 07, 1, 10, 15, 7, 38, tzinfo=pytz.UTC))
            with mock.patch.object(api, 'push') as push:
                api.send('foo', 'any')
                self.assertEqual(
                    '2014-07-01T11:15:07+00:00',
                    push.call_args_list[0][0][0]['expiration_time'])
                self.assertEqual(
                    '2014-07-01T11:15:07+00:00',
                    push.call_args_list[1][0][0]['expiration_time'])
