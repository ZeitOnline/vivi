from base64 import b64decode
from six.moves.urllib.parse import urlparse, parse_qs
import json
import mock
import plone.testing
import zeit.cms.testing
import zeit.content.author.honorar
import zeit.content.author.testing


HTTP_LAYER = zeit.cms.testing.HTTPLayer(
    zeit.cms.testing.RecordingRequestHandler,
    name='HTTPLayer', module=__name__)

LAYER = plone.testing.Layer(
    bases=(HTTP_LAYER, zeit.content.author.testing.ZOPE_LAYER),
    name='HDokLayer', module=__name__)


class HDokIntegration(zeit.cms.testing.FunctionalTestCase):

    layer = LAYER
    EMPTY_SEARCH_RESULT = json.dumps({'response': {'data': ''}})
    CREATE_RESULT = json.dumps({'response': {'scriptResult': 'myid'}})

    def setUp(self):
        super(HDokIntegration, self).setUp()
        self.api = zeit.content.author.honorar.Honorar(
            'http://localhost:%s' % self.layer['http_port'], 'user', 'pass')
        self.auth_token_patch = mock.patch.object(self.api, 'auth_token')
        token = self.auth_token_patch.start()
        token.return_value = 'token'
        self.http = self.layer['request_handler']

    def tearDown(self):
        if self.auth_token_patch._active_patches:
            self.auth_token_patch.stop()
        super(HDokIntegration, self).tearDown()

    def test_retrieves_auth_token(self):
        self.auth_token_patch.stop()
        self.http.response_codes = [200, 200]
        self.http.response_headers = [{'X-FM-Data-Access-Token': 'token'}, {}]
        self.http.response_body = ['', self.EMPTY_SEARCH_RESULT]
        self.assertEqual([], self.api.search('foo'))
        self.assertEqual('token', self.api.auth_token())
        self.assertEqual(2, len(self.http.requests))
        request = self.http.requests[-1]
        self.assertEqual('Bearer token', request['headers']['Authorization'])

    def test_search_passes_query_value(self):
        self.http.response_body = self.EMPTY_SEARCH_RESULT
        self.assertEqual([], self.api.search('foo'))
        request = json.loads(self.http.requests[0]['body'])
        self.assertEqual('foo', request['query'][0]['nameGesamt'])

    def test_create_b64encodes_parameters(self):
        self.http.response_body = self.CREATE_RESULT
        author = {'nachname': 'Shakespeare'}
        self.assertEqual('myid', self.api.create(author))
        query = parse_qs(urlparse(self.http.requests[0]['path']).query)
        params = json.loads(b64decode(query['script.param'][0]))
        self.assertEqual(author, params)


class HonorarIDTest(zeit.content.author.testing.FunctionalTestCase):

    def test_creates_author_in_hdok_if_no_external_id(self):
        author = zeit.content.author.author.Author()
        author.firstname = u'William'
        author.lastname = u'Shakespeare'
        self.repository['author'] = author
        self.assertTrue(self.layer['honorar_mock'].create.called)
        self.assertEqual(
            'mock-honorar-id', self.repository['author'].honorar_id)

    def test_honorar_id_present_is_left_alone(self):
        author = zeit.content.author.author.Author()
        author.firstname = u'William'
        author.lastname = u'Shakespeare'
        author.honorar_id = u'manual-id'
        self.repository['author'] = author
        self.assertFalse(self.layer['honorar_mock'].create.called)
        self.assertEqual('manual-id', self.repository['author'].honorar_id)
