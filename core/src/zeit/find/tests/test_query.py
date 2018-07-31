from datetime import datetime
from pytest import raises
from zeit.find.search import query


def test_simple_queries():
    assert query() == {
        'query': {'match_all': {}}}
    assert query(fulltext='Foo') == {
        'query': {'query_string': {'query': 'Foo'}}}
    assert query('Bar') == {
        'query': {'query_string': {'query': 'Bar'}}}
    assert query(authors='Foo Bar') == {
        'query': {'match': {'payload.document.author': 'Foo Bar'}}}
    assert query(from_=datetime(2009, 12, 19, 19, 9)) == {
        'query': {'range': {'payload.document.last-semantic-change': {
            'gte': '2009-12-19T19:09:00'}}}}
    assert query(until=datetime(2009, 12, 19, 19, 9)) == {
        'query': {'range': {'payload.document.last-semantic-change': {
            'lte': '2009-12-19T19:09:00'}}}}
    assert query(show_news=False) == {
        'query': {'bool': {'must_not': [
            {'match': {'payload.document.ressort': 'News'}},
            {'match': {'payload.workflow.product-id': 'News'}},
            {'match': {'payload.workflow.product-id': 'afp'}},
            {'match': {'payload.workflow.product-id': 'SID'}},
            {'match': {'payload.workflow.product-id': 'dpa-hamburg'}},
        ]}}}
    assert query(show_news=True) == {
        'query': {'match_all': {}}}
    assert query(types=[]) == {
        'query': {'match_all': {}}}
    assert query(types=['Foo', 'Bar']) == {
        'query': {'bool': {'should': [
            {'match': {'doc_type': 'Foo'}},
            {'match': {'doc_type': 'Bar'}},
        ]}}}
    assert query(keywords='Foo') == {
        'query': {'bool': {'should': [
            {'match': {'rtr_events': 'Foo'}},
            {'match': {'rtr_keywords': 'Foo'}},
            {'match': {'rtr_locations': 'Foo'}},
            {'match': {'rtr_organisations': 'Foo'}},
            {'match': {'rtr_persons': 'Foo'}},
            {'match': {'rtr_products': 'Foo'}},
        ]}}}


def test_combined_queries():
    assert query(fulltext='Foo', authors='Bar') == {
        'query': {'bool': {
            'must': [{'query_string': {'query': 'Foo'}}],
            'filter': [{'match': {'payload.document.author': 'Bar'}}],
        }}}
    assert query(
        from_=datetime(2009, 12, 19, 19, 9),
        until=datetime(2017, 5, 27, 20, 0)) == {
            'query': {'range': {'payload.document.last-semantic-change': {
                'gte': '2009-12-19T19:09:00', 'lte': '2017-05-27T20:00:00'}}}}
    assert query(show_news=False, fulltext='Foo') == {
        'query': {'bool': {
            'must': [{'query_string': {'query': 'Foo'}}],
            'must_not': [
                {'match': {'payload.document.ressort': 'News'}},
                {'match': {'payload.workflow.product-id': 'News'}},
                {'match': {'payload.workflow.product-id': 'afp'}},
                {'match': {'payload.workflow.product-id': 'SID'}},
                {'match': {'payload.workflow.product-id': 'dpa-hamburg'}},
            ]}}}
    assert query(year=2017, types=['Foo', 'Bar']) == {
        'query': {'bool': {'filter': [
            {'bool': {'should': [
                {'match': {'doc_type': 'Foo'}},
                {'match': {'doc_type': 'Bar'}},
            ]}},
            {'match': {'payload.document.year': 2017}},
        ]}}}


def test_erroneous_queries():
    with raises(ValueError):
        assert query(foo='bar')
    with raises(ValueError):
        assert query(filer_terms='foo')     # no longer supported
