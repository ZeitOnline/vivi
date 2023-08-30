# coding: utf8
from zeit.connector.dav.davresource import DAVResponse
from zeit.connector.dav.davxml import DavXmlDoc
import unittest


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
