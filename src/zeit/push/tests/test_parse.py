from zeit.push.testing import parse_settings as settings
import unittest
import zeit.push.parse


class ParseTest(unittest.TestCase):

    level = 2

    @unittest.skip(
        'Since Parse offers no REST API to retrieve push messages,'
        ' an automated integration test does not really work.')
    def test_push_works(self):
        api = zeit.push.parse.Connection(
            settings['application_id'], settings['rest_api_key'])
        api.send('Being pushy.', 'http://example.com', 'Clever title')

    def test_invalid_credentials_should_raise(self):
        api = zeit.push.parse.Connection('invalid', 'invalid')
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            api.send(None, None)
