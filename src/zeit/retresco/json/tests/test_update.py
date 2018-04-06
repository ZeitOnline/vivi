import json
import mock
import urllib2
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.retresco.testing


class TMSUpdateRequestTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.retresco.testing.ZCML_LAYER

    def setUp(self):
        super(TMSUpdateRequestTest, self).setUp()
        self.browser = zeit.cms.testing.Browser()

    def test_endpoint_avoids_get(self):
        b = self.browser
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 405: Method Not Allowed'):
            b.open('http://localhost/@@update_keywords')

    def test_endpoint_rejects_post_without_doc_ids(self):
        b = self.browser
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.post('http://localhost/@@update_keywords', '')
        with self.assertRaisesRegexp(urllib2.HTTPError,
                                     'HTTP Error 400: Bad Request'):
            b.post('http://localhost/@@update_keywords',
                   '{"foo" : "bar"}', 'application/x-javascript')

    def test_endpoint_calls_enrich_and_publish(self):
        b = self.browser
        with mock.patch('zeit.retresco.update.index') as index:
            b.post('http://localhost/@@update_keywords',
                   '{"doc_ids" : ['
                   '"{urn:uuid:9cb93717-2467-4af5-9521-25110e1a7ed8}", '
                   '"{urn:uuid:0da8cb59-1a72-4ae2-bbe2-006e6b1ff621}"]}',
                   'application/x-javascript')
            self.assertEqual({'message': 'OK'}, json.loads(b.contents))
            self.assertEqual('200 Ok', b.headers.getheader('status'))
            self.assertEqual(2, index.call_count)
            self.assertEqual(
                zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/online/2007/01/Somalia'),
                index.call_args[0][0])
            self.assertEqual(
                {'enrich': True, 'update_keywords': True, 'publish': True},
                index.call_args[1])

    def test_should_preserve_disabled_keywords(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        tagger = zeit.cms.tagging.interfaces.ITagger(article)
        tag = zeit.retresco.tag.Tag('Berlin', 'location')
        tagger[tag.code] = tag
        del tagger[tag.code]
        b = self.browser
        b.post('http://localhost/@@update_keywords',
               '{"doc_ids" : ['
               '"{urn:uuid:9cb93717-2467-4af5-9521-25110e1a7ed8}"]}',
               'application/x-javascript')
        self.assertEqual('200 Ok', b.headers.getheader('status'))
        self.assertEqual((tag.code,), tagger.disabled)
