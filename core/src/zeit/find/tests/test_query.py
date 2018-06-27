from datetime import datetime
from pytest import raises
from zeit.find.elastic import query


def test_simple_queries():
    assert query(fulltext='Foo') == {
        'query': {'query_string': {'query': 'Foo'}}}
    assert query(authors='Foo Bar') == {
        'query': {'match': {'payload.document.author': 'Foo Bar'}}}
    assert query(from_=datetime(2009, 12, 19, 19, 9)) == {
        'query': {'range': {'payload.document.last-semantic-change': {
            'gte': '2009-12-19T19:09:00'}}}}
    assert query(until=datetime(2009, 12, 19, 19, 9)) == {
        'query': {'range': {'payload.document.last-semantic-change': {
            'lte': '2009-12-19T19:09:00'}}}}


def test_combined_queries():
    assert query(fulltext='Foo', authors='Bar') == {
        'query': {'bool': {'must': [
            {'query_string': {'query': 'Foo'}},
            {'match': {'payload.document.author': 'Bar'}},
        ]}}}
    assert query(
        from_=datetime(2009, 12, 19, 19, 9),
        until=datetime(2017, 5, 27, 20, 0)) == {
            'query': {'range': {'payload.document.last-semantic-change': {
                'gte': '2009-12-19T19:09:00', 'lte': '2017-05-27T20:00:00'}}}}


def test_erroneous_queries():
    with raises(ValueError):
        assert query()
    with raises(ValueError):
        assert query(foo='bar')
