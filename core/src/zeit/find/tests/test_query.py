from pytest import raises
from zeit.find.elastic import query


def test_simple_queries():
    assert query(fulltext='Foo') == {
        'query': {'query_string': {'query': 'Foo'}}}
    assert query(authors='Foo Bar') == {
        'query': {'match': {'payload.document.author': 'Foo Bar'}}}


def test_combined_queries():
    assert query(fulltext='Foo', authors='Bar') == {
        'query': {'bool': {'must': [
            {'query_string': {'query': 'Foo'}},
            {'match': {'payload.document.author': 'Bar'}},
        ]}}}


def test_erroneous_queries():
    with raises(ValueError):
        assert query()
    with raises(ValueError):
        assert query(foo='bar')
