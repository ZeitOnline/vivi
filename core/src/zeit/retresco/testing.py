from unittest import mock
import copy
import importlib.resources
import json

import zope.app.appsetup.product

import zeit.cms.content.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.link.testing
import zeit.find.testing
import zeit.wochenmarkt.testing


HTTP_LAYER = zeit.cms.testing.HTTPLayer(zeit.cms.testing.RecordingRequestHandler)


class ProductConfigLayer(zeit.cms.testing.ProductConfigLayer):
    def __init__(self, config, **kw):
        # pytest may setUp/tearDown the same layer multiple times, so we have to
        # perform the `port` replacement each time.
        self.raw_config = copy.deepcopy(config)
        super().__init__(config, **kw)

    def setUp(self):
        for key, value in self.raw_config.items():
            if '{port}' in value:
                self.config[key] = value.format(port=self['http_port'])
        super().setUp()


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = ProductConfigLayer(
    {
        'base-url': 'http://localhost:{port}',
        'elasticsearch-url': 'http://tms-backend.staging.zeit.de:80/elasticsearch',
        'elasticsearch-index': 'zeit_pool',
        'elasticsearch-connection-class': 'zeit.retresco.search.Connection',
        'topic-redirect-prefix': 'http://www.zeit.de',
        'index-principal': 'zope.user',
        'kpi-fields': f'file://{HERE}/tests/kpi.xml',
        'topicpages-source': f'file://{HERE}/tests/topicpages.xml',
        'topicpage-prefix': '/thema',
    },
    bases=(
        HTTP_LAYER,
        zeit.content.article.testing.CONFIG_LAYER,
        zeit.content.link.testing.CONFIG_LAYER,
        zeit.content.volume.testing.CONFIG_LAYER,
        zeit.wochenmarkt.testing.CONFIG_LAYER,
    ),
)


class ElasticsearchMockLayer(zeit.cms.testing.Layer):
    def setUp(self):
        self['elasticsearch_mocker'] = mock.patch('elasticsearch.Elasticsearch.search')
        self['elasticsearch'] = self['elasticsearch_mocker'].start()
        response = (
            importlib.resources.files('zeit.retresco.tests') / 'elasticsearch_result.json'
        ).read_text('utf-8')
        self['elasticsearch'].return_value = json.loads(response)

    def tearDown(self):
        del self['elasticsearch']
        self['elasticsearch_mocker'].stop()
        del self['elasticsearch_mocker']


ELASTICSEARCH_MOCK_LAYER = ElasticsearchMockLayer()


class TMSMockLayer(zeit.cms.testing.Layer):
    def setUp(self):
        registry = zope.component.getGlobalSiteManager()
        self['old_tms'] = registry.queryUtility(zeit.retresco.interfaces.ITMS)
        self['tms_mock'] = mock.Mock()
        self['tms_mock'].url = 'http://tms.example.com'
        self['tms_mock'].get_article_topiclinks.return_value = []
        registry.registerUtility(self['tms_mock'], zeit.retresco.interfaces.ITMS)

    def tearDown(self):
        del self['tms_mock']
        if self['old_tms'] is not None:
            zope.component.getGlobalSiteManager().registerUtility(
                self['old_tms'], zeit.retresco.interfaces.ITMS
            )
        del self['old_tms']

    def testTearDown(self):
        self['tms_mock'].reset_mock()


TMS_MOCK_LAYER = TMSMockLayer()


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)

CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(ZOPE_LAYER)
CELERY_LAYER.queues += ('search',)


MOCK_LAYER = zeit.cms.testing.Layer(
    bases=(ZOPE_LAYER, ELASTICSEARCH_MOCK_LAYER),
    name='MockLayer',
)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class TagTestHelpers:
    """Helper to prefill DAV-Property used for keywords of a content object."""

    def set_tags(self, content, xml):
        """Prefill DAV-Property for keywords of `content` with `xml`.

        It inserts `xml` into a newly created DAV-property in the
        the 'tagging' namespace. `xml` is a string containing XML
        representing `Tag` objects, which requires `type` and `text`::

            <tag type="Person">Karen Duve</tag>
            <tag type="Location">Berlin</tag>

        """

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        name, ns = dav_key = zeit.retresco.tagger.KEYWORD_PROPERTY
        dav[dav_key] = """<ns:rankedTags xmlns:ns="{ns}">
        <rankedTags>{0}</rankedTags></ns:rankedTags>""".format(xml, ns=ns)


def create_testcontent():
    content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
    content.uniqueId = 'http://xml.zeit.de/testcontent'
    content.teaserText = 'teaser'
    content.title = 'title'
    zeit.cms.content.interfaces.IUUID(content).id = 'myid'
    return content
