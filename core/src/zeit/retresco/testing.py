from __future__ import absolute_import
import gocept.httpserverlayer.custom
import json
import mock
import pkg_resources
import plone.testing
import zeit.cms.content.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.content.article.testing
import zeit.content.image.testing
import zeit.content.link.testing
import zeit.content.volume.testing
import zeit.find.testing
import zeit.push.testing
import zeit.workflow.testing


HTTP_LAYER = zeit.cms.testing.HTTPLayer(
    zeit.cms.testing.RecordingRequestHandler,
    name='HTTPLayer', module=__name__)


product_config = """
<product-config zeit.retresco>
    base-url http://localhost:[PORT]
    elasticsearch-url http://tms-backend.staging.zeit.de:80/elasticsearch
    elasticsearch-index zeit_pool
    elasticsearch-connection-class zeit.retresco.search.Connection
    topic-redirect-prefix http://www.zeit.de
    index-principal zope.user
</product-config>
"""


class ElasticsearchMockLayer(plone.testing.Layer):

    def setUp(self):
        self['elasticsearch_mocker'] = mock.patch(
            'elasticsearch.client.Elasticsearch.search')
        self['elasticsearch'] = self['elasticsearch_mocker'].start()
        filename = pkg_resources.resource_filename(
            'zeit.retresco.tests', 'elasticsearch_result.json')
        with open(filename) as response:
            self['elasticsearch'].return_value = json.load(response)

    def tearDown(self):
        del self['elasticsearch']
        self['elasticsearch_mocker'].stop()
        del self['elasticsearch_mocker']


ELASTICSEARCH_MOCK_LAYER = ElasticsearchMockLayer()


class TMSMockLayer(plone.testing.Layer):

    def setUp(self):
        self['tms_mock'] = mock.Mock()
        self['tms_mock'].url = 'http://tms.example.com'
        self['tms_mock'].get_article_keywords.return_value = []
        self['tms_zca'] = gocept.zcapatch.Patches()
        self['tms_zca'].patch_utility(
            self['tms_mock'], zeit.retresco.interfaces.ITMS)

    def tearDown(self):
        self['tms_zca'].reset()
        del self['tms_zca']
        del self['tms_mock']

    def testTearDown(self):
        self['tms_mock'].reset_mock()


TMS_MOCK_LAYER = TMSMockLayer()


class ZCMLLayer(zeit.cms.testing.ZCMLLayer):

    defaultBases = zeit.cms.testing.ZCMLLayer.defaultBases + (HTTP_LAYER,)

    def setUp(self):
        self.product_config = self.product_config.replace(
            '[PORT]', str(self['http_port']))
        super(ZCMLLayer, self).setUp()


ZCML_LAYER = ZCMLLayer(
    'ftesting.zcml', product_config=zeit.cms.testing.cms_product_config +
    product_config +
    zeit.find.testing.product_config +
    zeit.push.testing.product_config +
    zeit.workflow.testing.product_config +
    zeit.content.article.testing.product_config +
    zeit.content.link.testing.product_config +
    zeit.content.volume.testing.product_config +
    zeit.content.image.testing.product_config)


CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(
    name='CeleryLayer', bases=(ZCML_LAYER,))
CELERY_LAYER.queues += ('search',)


MOCK_ZCML_LAYER = plone.testing.Layer(
    bases=(ZCML_LAYER, ELASTICSEARCH_MOCK_LAYER), name='MockZCMLLayer',
    module=__name__)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER


class TagTestHelpers(object):
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
        <rankedTags>{0}</rankedTags></ns:rankedTags>""".format(
            xml, ns=ns, tag=name)


def create_testcontent():
    content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
    content.uniqueId = 'http://xml.zeit.de/testcontent'
    content.teaserText = 'teaser'
    content.title = 'title'
    zeit.cms.content.interfaces.IUUID(content).id = 'myid'
    return content
