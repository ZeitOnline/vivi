from unittest import mock
import copy
import importlib.resources
import json

import pendulum
import zope.app.appsetup.product
import zope.event

from zeit.content.article.article import Article
from zeit.content.article.interfaces import IArticle
from zeit.content.image.testing import create_image
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.connector.filesystem
import zeit.content.author.author
import zeit.content.link.testing
import zeit.find.testing
import zeit.wochenmarkt.testing


def create_fixture(repository):
    article = Article()
    zeit.cms.content.field.apply_default_values(article, IArticle)
    article.year = 2025
    article.title = 'Cookie monster'
    article.ressort = 'Politik'
    article.supertitle = 'Blue'
    article.subtitle = 'It ate all the cookies'
    article.teaserTitle = 'Cookie monster detained'
    article.teaserText = 'No cookies left'
    article.teaserSupertitle = 'Sesame Street News'
    article.copyrights = 'ZEIT'
    article.access = 'free'
    article.serie = (
        zeit.cms.content.interfaces.ICommonMetadata['serie'].source(None).find('Autotest')
    )
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))
    repository['article'] = article

    author = zeit.content.author.author.Author()
    author.firstname = 'William'
    author.lastname = 'Shakespeare'
    repository['author'] = author

    repository['imagefolder'] = zeit.cms.repository.folder.Folder()
    image = create_image()
    modified = zeit.cms.workflow.interfaces.IModified(image)
    modified.date_created = pendulum.datetime(2025, 11, 27, 10, 21, 8, 0)
    semantic = zeit.cms.content.interfaces.ISemanticChange(image)
    semantic.last_semantic_change = pendulum.datetime(2025, 11, 27, 10, 21, 8, 0)
    repository['imagefolder']['image'] = image


HTTP_LAYER = zeit.cms.testing.HTTPLayer()


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


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.SQLIsolationSavepointLayer(_zope_layer, create_fixture)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)

CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(
    zeit.cms.testing.SQLIsolationTruncateLayer(_zope_layer, create_fixture)
)
CELERY_LAYER.queues += ('search',)


MOCK_LAYER = zeit.cms.testing.Layer(
    bases=(ZOPE_LAYER, ELASTICSEARCH_MOCK_LAYER),
    name='MockLayer',
)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER

    def setUp(self):
        super().setUp()
        # Remove TMS requests triggered by e.g. ZopeLayer.testSetUp()
        self.layer['request_handler'].reset()


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
