from zeit.cms.redirect.connection import Lookup
import gocept.httpserverlayer.custom
import json
import unittest


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler):

    post_response_code = 200
    post_response_body = '{}'
    posts_received = []

    gets_received = []
    get_response_code = 200
    get_headers = {}

    def do_POST(self):
        length = int(self.headers['content-length'])
        self.posts_received.append({
            'path': self.path,
            'data': self.rfile.read(length),
            'headers': self.headers,
        })
        self.send_response(self.post_response_code)
        self.end_headers()
        self.wfile.write(self.post_response_body)

    def do_GET(self):
        self.gets_received.append({
            'path': self.path,
            'headers': self.headers,
        })
        self.send_response(self.get_response_code)
        for key, value in self.get_headers.items():
            self.send_header(key, value)
        self.end_headers()


REDIRECT_LAYER = gocept.httpserverlayer.custom.Layer(
    RequestHandler, name='RedirectLayer', module=__name__)


class LookupTest(unittest.TestCase):

    layer = REDIRECT_LAYER

    def test_find_sends_path_and_host_header(self):
        lookup = Lookup('http://%s/' % self.layer['http_address'])
        lookup.find('http://xml.zeit.de/foo')
        requests = self.layer['request_handler'].gets_received
        self.assertEqual(1, len(requests))
        self.assertEqual('/foo', requests[0]['path'])
        self.assertEqual('xml.zeit.de', requests[0]['headers']['Host'])

    def test_find_with_no_redirect_status_200_returns_none(self):
        lookup = Lookup('http://%s/' % self.layer['http_address'])
        self.assertEqual(None, lookup.find('http://xml.zeit.de/foo'))

    def test_find_with_redirect_status_301_returns_new_url(self):
        self.layer['request_handler'].get_response_code = 301
        self.layer['request_handler'].get_headers = {
            'Location': 'http://xml.zeit.de/bar'}
        lookup = Lookup('http://%s/' % self.layer['http_address'])
        self.assertEqual(
            'http://xml.zeit.de/bar', lookup.find('http://xml.zeit.de/foo'))

    def test_add_sends_path_in_post(self):
        lookup = Lookup('http://%s/' % self.layer['http_address'])
        lookup.rename('http://xml.zeit.de/foo', 'http://xml.zeit.de/bar')
        requests = self.layer['request_handler'].posts_received
        self.assertEqual(1, len(requests))
        self.assertEqual(
            {'source': '/foo', 'target': '/bar'},
            json.loads(requests[0]['data']))
