from base64 import b64decode
from unittest import mock
from urllib.parse import urlparse, parse_qs
import json
import plone.testing
import zeit.cms.testing
import zeit.content.author.honorar
import zeit.content.author.interfaces
import zeit.content.author.testing
import zope.component
import zope.event
import zope.lifecycleevent


HTTP_LAYER = zeit.cms.testing.HTTPLayer(
    zeit.cms.testing.RecordingRequestHandler, name='HTTPLayer', module=__name__
)

LAYER = plone.testing.Layer(
    bases=(HTTP_LAYER, zeit.content.author.testing.ZOPE_LAYER), name='HDokLayer', module=__name__
)


class HDokIntegration(zeit.cms.testing.FunctionalTestCase):
    layer = LAYER
    EMPTY_SEARCH_RESULT = json.dumps({'response': {'data': ''}})
    CREATE_RESULT = json.dumps(
        {'response': {'scriptResult': json.dumps({'anlage': 'ok', 'gcid': 'myid'})}}
    )

    def setUp(self):
        super().setUp()
        self.api = zeit.content.author.honorar.Honorar(
            'http://localhost:%s' % self.layer['http_port'], 'fake-invalid-url', 'user', 'pass'
        )
        self.auth_token_patch = mock.patch.object(self.api, 'auth_token')
        token = self.auth_token_patch.start()
        token.return_value = 'token'
        self.http = self.layer['request_handler']

    def tearDown(self):
        if self.auth_token_patch._active_patches:
            self.auth_token_patch.stop()
        super().tearDown()

    def test_retrieves_auth_token(self):
        self.auth_token_patch.stop()
        self.http.response_codes = [200, 200]
        self.http.response_headers = [{'X-FM-Data-Access-Token': 'token'}, {}]
        self.http.response_body = ['', self.EMPTY_SEARCH_RESULT]
        self.assertEqual([], self.api.search('foo'))
        self.assertEqual('token', self.api.auth_token('hdok'))
        self.assertEqual(2, len(self.http.requests))
        request = self.http.requests[-1]
        self.assertEqual('Bearer token', request['headers']['Authorization'])

    def test_search_passes_query_value(self):
        self.http.response_body = self.EMPTY_SEARCH_RESULT
        self.assertEqual([], self.api.search('foo'))
        request = json.loads(self.http.requests[0]['body'])
        self.assertEqual('foo', request['query'][0]['nameGesamtSuchtext'])

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
        author.firstname = 'William'
        author.lastname = 'Shakespeare'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(author))
        api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        self.assertTrue(api.create.called)
        self.assertEqual('mock-honorar-id', author.honorar_id)

    def test_honorar_id_present_is_left_alone(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'William'
        author.lastname = 'Shakespeare'
        author.honorar_id = 'manual-id'
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(author))
        api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        self.assertFalse(api.create.called)
        self.assertEqual('manual-id', author.honorar_id)

    def test_does_not_create_hdok_on_retract(self):
        api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        author = zeit.content.author.author.Author()
        author.firstname = 'William'
        author.lastname = 'Shakespeare'
        self.repository['author'] = author
        pub = zeit.cms.workflow.interfaces.IPublish(self.repository['author'])
        pub.publish(background=False)
        pub.retract(background=False)
        self.assertFalse(api.create.called)
