import json
import urllib2
import zeit.retresco.testing
import zeit.retresco.update
import zope.testbrowser.testing

class TMSUpdateRequestTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.retresco.testing.ZCML_LAYER

    def test_endpoint_avoids_get(self):
        b = zope.testbrowser.testing.Browser()
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 405: Method Not Allowed'):
            b.open('http://localhost/@@update_keywords')

    def test_endpoint_rejects_post_without_doc_ids(self):
        b = zope.testbrowser.testing.Browser()
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.post('http://localhost/@@update_keywords', '')
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.post('http://localhost/@@update_keywords',
                   '{"foo" : "bar"}', 'application/x-javascript')

    def test_endpoint_skips_invalid_doc_ids(self):
        b = zope.testbrowser.testing.Browser()
        b.post('http://localhost/@@update_keywords',
               '{"doc_ids" : [1, 2, 3]}', 'application/x-javascript')
        status = {
            'updated_content': [],
            'updated': [],
            'message': 'Nothing updated',
            'invalid': [1, 2, 3]}
        self.assertEquals(status, json.loads(b.contents))
        self.assertEquals('200 Ok', b.headers.getheader('status'))

    def test_endpoint_successful_update_vaild_article(self):
        b = zope.testbrowser.testing.Browser()
        b.post('http://localhost/@@update_keywords',
               '{"doc_ids" : ['
                '"{urn:uuid:9cb93717-2467-4af5-9521-25110e1a7ed8}", '
                '"{urn:uuid:0da8cb59-1a72-4ae2-bbe2-006e6b1ff621}"]}',
                'application/x-javascript')
        status = {
            'updated_content': ['http://xml.zeit.de/online/2007/01/Somalia',
                                'http://xml.zeit.de/online/2007/01/Somalia'],
            'updated': ['{urn:uuid:9cb93717-2467-4af5-9521-25110e1a7ed8}',
                        '{urn:uuid:0da8cb59-1a72-4ae2-bbe2-006e6b1ff621}'],
            'message': 'Update successful',
            'invalid': []}
        self.assertEquals(status, json.loads(b.contents))
        self.assertEquals('200 Ok', b.headers.getheader('status'))
