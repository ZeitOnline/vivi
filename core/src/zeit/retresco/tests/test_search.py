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

    def test_search_result_may_contain_payload_fields(self):
        result = self.elasticsearch.search(
            self.query, 'title:asc', rows=2, include_payload=True)
        self.assertEqual(
            'Islamismus', result[0]['payload']['body']['supertitle'])
