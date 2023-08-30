# coding: utf8
import unittest
import zeit.connector.dav.davbase


class TestURLEncode(unittest.TestCase):

    def setUp(self):
        self.conn = zeit.connector.dav.davbase.DAVConnection('foo.testing')

    def assertQuote(self, unquoted, quoted):
        self.assertEqual(quoted, self.conn.quote_uri(unquoted))

    def test_simple(self):
        self.assertQuote('http://foo.testing/bar/baz',
                         'http://foo.testing/bar/baz')

    def test_unicode_hostname(self):
        self.assertQuote('http://föö.testing/bar/baz',
                         'http://föö.testing/bar/baz')

    def test_unicode_path(self):
        self.assertQuote('http://foo.testing/bär/böz',
                         'http://foo.testing/b%C3%A4r/b%C3%B6z')

    def test_query_and_fragment_quoted_to_path(self):
        self.assertQuote('http://foo.testing/bar?a=b&c=d#fragment',
                         'http://foo.testing/bar%3Fa%3Db%26c%3Dd%23fragment')
