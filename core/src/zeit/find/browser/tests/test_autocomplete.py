from unittest import mock
from zeit.cms.browser.widget import AutocompleteSourceQuery
import unittest
import zeit.cms.testing
import zeit.find.testing
import zope.interface
import zope.publisher.browser


class TestSimpleFind(unittest.TestCase,
                     zeit.cms.testing.BrowserAssertions):

    layer = zeit.find.testing.WSGI_LAYER

    def setUp(self):
        from zeit.cms.testing import Browser
        self.browser = Browser(self.layer['wsgi_app'])
        self.browser.login('user', 'userpw')
        self.browser.open('http://localhost/++skin++vivi/')
        search_patch = mock.patch('zeit.find.search.Elasticsearch.search')
        self.addCleanup(search_patch.stop)
        self.search = search_patch.start()

    def test_no_query_should_return_empty_list(self):
        self.browser.open('@@simple_find')
        self.assert_json([])

    def test_given_term_should_query(self):
        self.search.return_value = []
        self.browser.open('@@simple_find?term=Search-Term')
        # ES applies the same analyzer (e.g. lowercase) to the search term
        # as to the field value during indexing, so we don't need to lowercase.
        self.search.assert_called_with(dict(query=dict(match_phrase_prefix={
            'payload.vivi.autocomplete': 'Search-Term'})))

    def test_given_types_should_be_passed_to_search(self):
        self.search.return_value = []
        self.browser.open(
            '@@simple_find?term=search-term&types:list=t1&types:list=t2')
        self.search.assert_called_with(
            dict(query=dict(bool=dict(must=[
                dict(match_phrase_prefix={
                    'payload.vivi.autocomplete': 'search-term'})
            ], filter=[
                dict(bool=dict(should=[
                    dict(match=dict(doc_type='t1')),
                    dict(match=dict(doc_type='t2')),
                ])),
            ]))))

    def test_given_parameters_should_be_passed_to_search(self):
        self.search.return_value = []
        self.browser.open(
            '@@simple_find?term=search-term&access=abo')
        self.search.assert_called_with(
            dict(query=dict(bool=dict(must=[
                dict(match_phrase_prefix={
                    'payload.vivi.autocomplete': 'search-term'})
            ], filter=[
                {'match': {'payload.document.access': 'abo'}}
            ]))))

    def test_query_result_should_be_returned(self):
        self.search.return_value = [
            dict(url='/A'),
            dict(url='/B')]
        self.browser.open('@@simple_find?term=search-term')
        self.assert_json(
            [{'label': '/A', 'value': 'http://xml.zeit.de/A'},
             {'label': '/B', 'value': 'http://xml.zeit.de/B'}])

    def test_test_title_should_become_label(self):
        self.search.return_value = [
            dict(url='/A', teaser='Teaser Title', title='Title')]
        self.browser.open('@@simple_find?term=search-term')
        self.assert_json([{'label': 'Title',
                           'value': 'http://xml.zeit.de/A'}])

    def test_title_should_become_label_if_no_teaser_title(self):
        self.search.return_value = [dict(url='/A', title='Title')]
        self.browser.open('@@simple_find?term=search-term')
        self.assert_json([{'label': 'Title', 'value': 'http://xml.zeit.de/A'}])

    def test_query_view_should_render_input(self):
        @zope.interface.implementer(
            zeit.cms.content.interfaces.IAutocompleteSource)
        class FakeSource:
            def get_check_types(self):
                return ('t1', 't2', 't3')

        view = AutocompleteSourceQuery(
            FakeSource(), zope.publisher.browser.TestRequest(
                skin=zeit.cms.browser.interfaces.ICMSLayer))
        self.assertEllipsis(
            ('<input type="text" class="autocomplete" '
             'placeholder="Type to find entries ..." '
             'cms:autocomplete-source="'
             '...?types%3Alist=t1&types%3Alist=t2&types%3Alist=t3" />'),
            view())
