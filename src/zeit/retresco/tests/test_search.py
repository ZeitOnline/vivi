from ..interfaces import IElasticsearch
from zeit.cms.interfaces import IResult
import unittest
import zeit.retresco.testing
import zope.component


class TestElasticsearch(unittest.TestCase):
    """Testing ..search.Elasticsearch."""

    layer = zeit.retresco.testing.MOCK_ZCML_LAYER

    query = {
        "query": {
            "query_string": {
                "query": "Salafisten"
            }
        }
    }

    def setUp(self):
        super(TestElasticsearch, self).setUp()
        self.elasticsearch = zope.component.getUtility(IElasticsearch)

    def test_search_returns_a_result_object(self):
        result = self.elasticsearch.search(self.query, 'title:asc', rows=2)
        self.assertTrue(IResult.providedBy(result))
        self.assertEqual(5, result.hits)

    def test_search_result_contains_uniqueId__doc_id__and__doc_type(self):
        result = self.elasticsearch.search(self.query, 'title:asc', rows=2)
        self.assertEqual(
            [{'doc_id': u'{urn:uuid:9cb93717-2467-4af5-9521-25110e1a7ed8}',
              'doc_type': u'video',
              'uniqueId': 'http://xml.zeit.de/video/2016-07/5020444524001'},
             {'doc_id': u'{urn:uuid:0da8cb59-1a72-4ae2-bbe2-006e6b1ff621}',
              'doc_type': u'article',
              'uniqueId': 'http://xml.zeit.de/zeit-magazin/2015/09/'
                          'dinslaken-ruhrgebiet-islamischer-staat-'
                          'salafismus'}],
            result)

    def test_search_result_may_contain_payload_fields(self):
        result = self.elasticsearch.search(
            self.query, 'title:asc', rows=2, include_payload=True)
        self.assertIn(('supertitle', 'Islamismus'), result[0].items())
