# coding: utf8
from io import BytesIO
import unittest
import zeit.connector.dav.davbase
import zeit.connector.dav.davconnection
import zeit.connector.dav.interfaces


class TestPropfind(unittest.TestCase):

    response = ''

    def setUp(self):
        self.count = 0
        self.conn = zeit.connector.dav.davconnection.DAVConnection(
            'localhost')
        self._orig_propfind = zeit.connector.dav.davbase.DAVConnection.propfind
        zeit.connector.dav.davbase.DAVConnection.propfind = self.propfind

    def tearDown(self):
        zeit.connector.dav.davbase.DAVConnection.propfind = self._orig_propfind

    def propfind(self, *args, **kwargs):
        self.count += 1
        result = BytesIO(self.response.encode('utf-8'))
        result.status = 207
        result.reason = 'Multi Status'
        result.getheader = lambda x, y=None: y
        return result

    def test_propfind_retries_incomplete_results(self):
        self.verifyRaisesAfter('<a><b></b>', 3)

    def test_xml_errors_raise(self):
        self.verifyRaisesAfter('garbage', 1)
        self.verifyRaisesAfter('<a>&</a>', 1)

    def test_valid_returns_result(self):
        self.response = '<a><b/></a>'
        result = self.conn.propfind('/')
        self.assertEqual(207, result.status)

    def verifyRaisesAfter(self, xml, count):
        self.response = xml
        self.assertRaises(zeit.connector.dav.interfaces.DavXmlParseError,
                          self.conn.propfind, '/')
        self.assertEqual(count, self.count)
        self.count = 0


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


class TestDAVResponse(unittest.TestCase):

    RESPONSE_TEMPLATE = """\
<D:multistatus xmlns:D="DAV:" xmlns:ns0="DAV:">
<D:response
    xmlns:CMS="http://namespaces.zeit.de/CMS"
    xmlns:g0="http://namespaces.zeit.de/CMS/document"
    xmlns:g1="http://namespaces.zeit.de/CMS/lifetimecounter"
    xmlns:g2="http://namespaces.zeit.de/CMS/meta"
    xmlns:g3="http://namespaces.zeit.de/CMS/workflow"
    xmlns:lp1="DAV:"
    xmlns:lp2="http://apache.org/dav/props/">
<D:href>%s</D:href>
<D:propstat>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
</D:multistatus>
"""

    def get_response(self, url):
        from zeit.connector.dav.davresource import DAVResponse
        from zeit.connector.dav.davxml import DavXmlDoc
        doc = DavXmlDoc()
        doc.from_string(self.RESPONSE_TEMPLATE % url)
        return DAVResponse(doc, doc.get_response_nodes()[0])

    def test_response_should_decode_urlencoded_urls(self):
        self.assertEqual('/foo bar', self.get_response('/foo%20bar').url)

    def test_response_should_decode_utf8_in_urlencode(self):
        self.assertEqual('/foobär', self.get_response('/foob%C3%A4r').url)

    def test_response_should_handle_unicode_urls(self):
        self.assertEqual('/foobär', self.get_response('/foobär').url)

    def test_response_should_handle_unicode_urls_with_quoting(self):
        self.assertEqual('/foo bär', self.get_response('/foo%20bär').url)


class TestDAVResource(unittest.TestCase):

    def test_entities_in_url_may_be_part_of_the_path(self):
        from zeit.connector.dav.davresource import DAVResource
        res = DAVResource('http://example.com/parks_&amp;_recreation')
        self.assertEqual('/parks_&amp;_recreation', res.path)
