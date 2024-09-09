from unittest import mock
import copy
import json
import logging
import os.path

import plone.testing
import requests_mock
import zope.component

from zeit.cms.repository.folder import Folder
import zeit.cms.testing
import zeit.connector.interfaces
import zeit.content.article.testing
import zeit.content.author.author
import zeit.newsimport.interfaces
import zeit.retresco.testhelper
import zeit.retresco.testing
import zeit.workflow.testing


HERE = os.path.dirname(__file__)


def asset_path(*parts):
    return os.path.join(HERE, 'tests', 'data', *parts)


CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'weblines-url': 'http://dpa_api_test.com',
        'nextline-url': 'http://dpa_api_test.com',
        'dpa-rubric-config-source': f'file://{HERE}/tests/data/products.xml',
    },
    bases=(zeit.retresco.testing.CONFIG_LAYER,),
)
# NOTE author config layer is included in article config layer
# NOTE article config layer is included in retresco config layer
ZCML_LAYER = zeit.cms.testing.ZCMLLayer(config_file='ftesting.zcml', bases=(CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER, zeit.retresco.testhelper.TMS_MOCK_LAYER))


class DPALayer(plone.testing.Layer):
    name = 'DPALayer'
    module = None

    url = 'http://dpa_api_test.com'
    dpa_entries = json.load(open(asset_path('entries.json')))

    def setUp(self):
        logging.getLogger('zeit.newsimport.news').setLevel(logging.INFO)
        self['entries'] = copy.deepcopy(self.dpa_entries)
        self['dpa_api_mock'] = r_mock = requests_mock.Mocker()
        self['dpa_api_get'] = r_mock.register_uri(
            'GET', '{}/entries.json'.format(self.url), json=copy.deepcopy(self['entries'])
        )
        # NOTE _wireq_receipt is way longer irl ~375 characters
        self['dpa_api_delete'] = r_mock.register_uri(
            'DELETE', '{}/entry/AQEB93'.format(self.url), status_code=204
        )
        self['dpa_api_mock'].__enter__()

    def tearDown(self):
        self['dpa_api_mock'].__exit__(None, None, None)
        del self['dpa_api_mock']

    def testSetUp(self):
        self['entries'] = copy.deepcopy(self.dpa_entries)


DPA_LAYER = DPALayer(name='DPALayer', bases=(ZOPE_LAYER,))


class FunctionalAPITestCase(zeit.cms.testing.FunctionalTestCase):
    layer = DPA_LAYER


class DPAMockLayer(plone.testing.Layer):
    name = 'DPAMockLayer'
    module = None

    dpa_entries = json.load(open(asset_path('entries.json')))
    image = asset_path('urn_newsml_dpa.com_20090101_220202-99-942804-v3-s2048.jpeg')

    def setUp(self):
        logging.getLogger('zeit.newsimport.news').setLevel(logging.INFO)
        registry = zope.component.getGlobalSiteManager()
        self['dpa_entries'] = copy.deepcopy(self.dpa_entries)
        self['dpa_mock'] = mock.Mock()
        self['dpa_mock'].get_entries.side_effect = lambda *args, **kw: self['dpa_entries'][
            'entries'
        ]

        self['dpa_previous'] = registry.queryUtility(
            zeit.newsimport.interfaces.IDPA, name='weblines'
        )
        registry.registerUtility(self['dpa_mock'], zeit.newsimport.interfaces.IDPA, name='weblines')

        self['dpa_article_id'] = 'http://xml.zeit.de/news/2021-12/15/beispielmeldung-ueberschrift'

    def tearDown(self):
        del self['dpa_mock']
        registry = zope.component.getGlobalSiteManager()
        registry.registerUtility(
            self['dpa_previous'], zeit.newsimport.interfaces.IDPA, name='weblines'
        )
        del self['dpa_previous']

    def testSetUp(self):
        def callback(*args):
            with open(self.image, 'rb') as fd:
                image_bytes = fd.read()
            return image_bytes

        self['dpa_entries'] = copy.deepcopy(self.dpa_entries)

        image_entry = self['dpa_entries']['entries'][-1]['associations'][0]
        self['image_server_mock'] = r_mock = requests_mock.Mocker()
        self['image_get'] = r_mock.register_uri(
            'GET', image_entry['renditions'][0]['url'], content=callback
        )
        self['image_server_mock'].__enter__()

    def testTearDown(self):
        self['image_server_mock'].__exit__(None, None, None)
        del self['image_server_mock']
        self['dpa_mock'].reset_mock()


DPA_MOCK_LAYER = DPAMockLayer(name='DPAMockLayer', bases=(ZOPE_LAYER,))
CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(name='CeleryLayer', bases=(DPA_MOCK_LAYER,))
CELERY_LAYER.queues += ('search',)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = DPA_MOCK_LAYER

    def setUp(self):
        super().setUp()
        agency = zeit.content.author.author.Author()
        agency.firstname = 'dpa'
        self.repository['autoren'] = Folder()
        self.repository['autoren']['dpa'] = agency
        self.dpa = zope.component.getUtility(zeit.newsimport.interfaces.IDPA, name='weblines')
        self.news = zeit.newsimport.news.ArticleEntry(self.dpa.get_entries()[0])

        self.connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        self.connector.search_result = []

    def add_article_with_image(self):
        entry = self.dpa.get_entries()[-1].copy()
        news = zeit.newsimport.news.ArticleEntry(entry)
        return news.publish(news.create())
