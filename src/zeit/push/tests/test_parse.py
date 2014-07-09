from datetime import datetime
from zeit.push.testing import parse_settings as settings
import mock
import pytz
import unittest
import zeit.push.parse


class ParseTest(unittest.TestCase):

    level = 2

    @unittest.skip(
        'Since Parse offers no REST API to retrieve push messages,'
        ' an automated integration test does not really work.')
    def test_push_works(self):
        api = zeit.push.parse.Connection(
            settings['application_id'], settings['rest_api_key'], 1)
        api.send('Being pushy.', 'http://example.com')

    def test_invalid_credentials_should_raise(self):
        api = zeit.push.parse.Connection('invalid', 'invalid', 1)
        with self.assertRaises(zeit.push.interfaces.WebServiceError):
            api.send('Being pushy.', 'http://example.com')


class URLRewriteTest(unittest.TestCase):

    def rewrite(self, url):
        return zeit.push.parse.Connection.rewrite_url(url)

    def test_www_zeit_de_is_replaced_with_wrapper(self):
        self.assertEqual(
            'http://wrapper.zeit.de/foo/bar',
            self.rewrite('http://www.zeit.de/foo/bar'))

    def test_blog_zeit_de_is_replaced_with_wrapper_and_appends_query(self):
        self.assertEqual(
            'http://wrapper.zeit.de/blog/foo/bar?feed=articlexml',
            self.rewrite('http://blog.zeit.de/foo/bar'))

    def test_zeit_de_blog_is_replaced_with_wrapper_and_appends_query(self):
        self.assertEqual(
            'http://wrapper.zeit.de/blog/foo/bar?feed=articlexml',
            self.rewrite('http://www.zeit.de/blog/foo/bar'))


class ExpirationTest(unittest.TestCase):

    def test_sets_expiration_time(self):
        api = zeit.push.parse.Connection(
            'any', 'any', 3600)
        with mock.patch('zeit.push.parse.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2014, 07, 1, 10, 15, tzinfo=pytz.UTC)
            with mock.patch.object(api, 'push') as push:
                api.send('foo', 'any')
                data = push.call_args[0][0]
                self.assertEqual(
                    '2014-07-01T11:15:00+00:00', data['expiration_time'])
