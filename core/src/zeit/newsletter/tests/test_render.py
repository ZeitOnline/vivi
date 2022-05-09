from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.newsletter.render import Renderer
import gocept.httpserverlayer.custom
import urllib.parse
import time
import unittest


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler):

    response_code = 200
    requests = []
    sleep = 0

    def do_GET(self):
        self.requests.append(dict(
            path=self.path,
            headers=self.headers,
        ))
        time.sleep(self.sleep)

        # dear stdlib, you've got to be kidding
        query = urllib.parse.parse_qs(
            urllib.parse.urlparse('http://host' + self.path).query)
        format = query.get('format', [''])[0]
        response = format

        if response:
            self.send_response(self.response_code)
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'error')


HTTP_LAYER = gocept.httpserverlayer.custom.Layer(
    RequestHandler, name='HTTPLayer', module=__name__)


class RendererTest(unittest.TestCase):

    layer = HTTP_LAYER

    def test_converts_uniqueId_to_rendering_host(self):
        content = ExampleContentType()
        content.uniqueId = 'http://xml.zeit.de/foo/bar'
        renderer = Renderer('http://example.com:8080')
        self.assertEqual('http://example.com:8080/foo/bar',
                         renderer.url(content))

    def test_host_with_trailing_slash_yields_correct_url(self):
        content = ExampleContentType()
        content.uniqueId = 'http://xml.zeit.de/foo/bar'
        renderer = Renderer('http://example.com:8080/')
        self.assertEqual('http://example.com:8080/foo/bar',
                         renderer.url(content))

    def test_returns_html_and_plain_text(self):
        content = ExampleContentType()
        content.uniqueId = 'http://xml.zeit.de/foo/bar'
        renderer = Renderer('http://localhost:%s' % self.layer['http_port'])
        result = renderer(content)
        self.assertEqual('html', result['html'])
        self.assertEqual('txt', result['text'])
