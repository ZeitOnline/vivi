from ..interfaces import IElasticsearch
from zeit.cms.interfaces import IResult
import json
import unittest
import zeit.retresco.testing
import zope.component


class TestElasticsearch(unittest.TestCase):
    """Testing ..search.Elasticsearch."""

    layer = zeit.retresco.testing.MOCK_LAYER

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

    def test_search_result_may_contain_specific_source(self):
        query = self.query.copy()
        query['_source'] = ['payload.teaser.title', 'payload.body.title']
        self.elasticsearch.search(query, 'title:asc', rows=2)
        call_body = self.elasticsearch.client.search.call_args[1]['body']
        self.assertEqual(query['_source'], json.loads(call_body)['_source'])

    def test_search_rejects_specific_source_and_payload_flag(self):
        query = self.query.copy()
        query['_source'] = ['payload.teaser.title', 'url', 'rtr_keyword']
        with self.assertRaises(ValueError):
            self.elasticsearch.search(query, 'date:asc', include_payload=True)
