from zeit.cms.browser.widget import AutocompleteSourceQuery
import mock
import unittest
import zeit.cms.testing
import zeit.find.tests
import zope.interface
import zope.publisher.browser


class TestSimpleFind(unittest.TestCase,
                     zeit.cms.testing.BrowserAssertions):

    layer = zeit.find.tests.LAYER

    def setUp(self):
        from zope.testbrowser.testing import Browser
        self.browser = Browser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')
        self.browser.open('http://localhost/++skin++vivi/')
        search_patch = mock.patch('zeit.find.search.search')
        self.addCleanup(search_patch.stop)
        self.search = search_patch.start()

    def test_no_query_should_return_empty_list(self):
        self.browser.open('@@simple_find')
        self.assert_json([])

    def test_given_term_should_query_solr(self):
        self.search.return_value = []
        self.browser.open('@@simple_find?term=Search-Term')
        self.search.assert_called_with(
            u'((title:(search-term*) OR title:(search-term)))')

    def test_given_types_should_be_passed_to_solr(self):
        self.search.return_value = []
        self.browser.open(
            '@@simple_find?term=search-term&types:list=t1&types:list=t2')
        self.search.assert_called_with(
            u'((title:(search-term*) OR title:(search-term)) AND (type:(t1) '
            'OR type:(t2)))')

    def test_query_result_should_be_returned(self):
        self.search.return_value = [
            dict(uniqueId='A'),
            dict(uniqueId='B')]
        self.browser.open('@@simple_find?term=search-term')
        self.assert_json(
            [{'value': 'A', 'label': 'A'}, {'value': 'B', 'label': 'B'}])

    def test_test_title_should_become_label(self):
        self.search.return_value = [
            dict(uniqueId='A', teaser_title='Teaser Title', title='Title')]
        self.browser.open('@@simple_find?term=search-term')
        self.assert_json([{'label': 'Teaser Title', 'value': 'A'}])

    def test_title_should_become_label_if_no_teaser_title(self):
        self.search.return_value = [dict(uniqueId='A', title='Title')]
        self.browser.open('@@simple_find?term=search-term')
        self.assert_json([{'label': 'Title', 'value': 'A'}])

    def test_query_view_should_render_input(self):
        source = mock.Mock()
        source.get_check_types.return_value = ('t1', 't2', 't3')
        zope.interface.alsoProvides(
            source, zeit.cms.content.interfaces.IAutocompleteSource)
        view = AutocompleteSourceQuery(
            source, zope.publisher.browser.TestRequest(
                skin=zeit.cms.browser.interfaces.ICMSLayer))
        self.assertEllipsis(
            ('<input type="text" class="autocomplete" '
             'placeholder="Type to find entries ..." '
             'cms:autocomplete-source="'
             '...?types%3Alist=t1&types%3Alist=t2&types%3Alist=t3" />'),
            view())
