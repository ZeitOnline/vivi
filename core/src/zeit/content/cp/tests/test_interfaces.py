from zeit.cms.testing import copy_inherited_functions
import gocept.testing.assertion
import mock
import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.cp.interfaces
import zeit.content.cp.testing


class CPSourceTest(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    source = zeit.content.cp.interfaces.centerPageSource
    expected_types = ['centerpage-2009']

    copy_inherited_functions(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        locals())


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

    def test_automatic_using_solr_requires_no_referenced_centerpage(self):
        self.area.automatic_type = 'query'
        self.area.raw_query = 'foo'
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
        with self.assertRaises(zeit.cms.interfaces.ValidationError) as err:
            self.interface.validateInvariants(self.area)
        self.assertIn('No JSON object could be decoded', str(err.exception))
