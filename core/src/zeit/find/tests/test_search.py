from unittest import TestCase
from zope.component import getUtility
from zeit.cms.testing import FunctionalTestCase
from zeit.find.interfaces import ICMSSearch
from zeit.find.testing import LAYER


class TestElasticsearch(TestCase):
    layer = LAYER

    def test_cms_search_utility(self):
        cms_search = getUtility(ICMSSearch)
        assert cms_search.index == 'foo_pool'


class QueryTest(FunctionalTestCase):
    layer = LAYER

    def test_query(self):
        import zeit.find.search

        self.layer.set_result(__package__, 'data/obama.json')
        elastic = getUtility(ICMSSearch)
        q = zeit.find.search.query('Obama')
        result = elastic.search(q)
        self.assertEqual(37002, result.hits)
        self.assertEqual(
            '/2018/25/donald-trump-golf-schummeln-golfplatz-weltpolitik', result[-1]['url']
        )
        req = self.layer.search.client.search
        self.assertEqual(1, req.call_count)

    def test_suggest(self):
        NotImplemented
