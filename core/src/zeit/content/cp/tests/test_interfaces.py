from unittest import mock
import gocept.testing.assertion
import unittest
import zeit.content.cp.interfaces
import zeit.content.cp.testing


class AreaValidationTest(
        unittest.TestCase,
        gocept.testing.assertion.Exceptions):

    def setUp(self):
        super(AreaValidationTest, self).setUp()
        self.interface = zeit.content.cp.interfaces.IArea
        self.area = mock.Mock()
        self.area.count = 3
        self.area.automatic = True

    def test_automatic_from_centerpage_requires_referenced_centerpage(self):
        self.area.automatic_type = 'centerpage'
        self.area.referenced_cp = None
        with self.assertRaises(zeit.cms.interfaces.ValidationError):
            self.interface.validateInvariants(self.area)

    def test_automatic_using_other_requires_no_referenced_centerpage(self):
        self.area.automatic_type = 'elasticsearch-query'
        self.area.elasticsearch_raw_query = '{"query": {}}'
        self.area.referenced_cp = None
        with self.assertNothingRaised():
            self.interface.validateInvariants(self.area)

    def test_automatic_from_elasticsearch_requires_raw_query(self):
        self.area.automatic_type = 'elasticsearch-query'
        self.area.elasticsearch_raw_query = None
        with self.assertRaises(zeit.cms.interfaces.ValidationError) as err:
            self.interface.validateInvariants(self.area)
        self.assertIn(
            'Automatic area with teaser from elasticsearch query',
            str(err.exception))

    def test_elasticsearch_raw_query_requires_valid_json(self):
        self.area.automatic_type = 'elasticsearch-query'
        self.area.elasticsearch_raw_query = 'this is no json'
        with self.assertRaises(zeit.cms.interfaces.ValidationError):
            self.interface.validateInvariants(self.area)


class TopicpageFilterSourceTest(zeit.content.cp.testing.FunctionalTestCase):

    def test_parses_filter_json(self):
        self.assertEqual(
            ['videos'],
            list(zeit.contentquery.interfaces.TopicpageFilterSource()))
