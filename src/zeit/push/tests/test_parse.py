from zeit.push.interfaces import PARSE_NEWS_CHANNEL
import mock
import os
import unittest
import zeit.push.parse
import zeit.push.testing
import zope.app.appsetup.product


class ParseTest(unittest.TestCase):

    level = 2
    layer = zeit.push.testing.ZCML_LAYER

    def setUp(self):
        self.app_id = os.environ['ZEIT_PUSH_PARSE_APP_ID']
        self.api_key = os.environ['ZEIT_PUSH_PARSE_API_KEY']

    def test_push_works(self):
        # Parse offers no REST API to retrieve push messages,
        # so this is just a smoke test.
        api = zeit.push.parse.Connection(
            self.app_id, self.api_key, 1)
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

    def test_friedbert_version_links_to_app_content(self):
        api = zeit.push.parse.Connection(None, None, 1)
        with mock.patch.object(api, 'push') as push:
            api.send('', 'http://www.zeit.de/bar', channels=PARSE_NEWS_CHANNEL)
            android = push.call_args_list[0][0][0]
            self.assertEqual(
                'http://www.zeit.de/bar',
                android['data']['url'].split('?')[0])
            ios = push.call_args_list[1][0][0]
            self.assertEqual(
                'http://www.zeit.de/bar',
                ios['data']['aps']['url'].split('?')[0])

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
