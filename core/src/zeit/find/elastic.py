from zope.component import getUtility
from zeit.retresco.interfaces import IElasticsearch


builders = {}


def search(query, sort_order=None, additional_result_fields=(), rows=50, **kw):
    """Search elasticsearch according to query."""
    if query is None:
        return []
    elasticsearch = getUtility(IElasticsearch)
    return elasticsearch.search(query, rows=rows, **kw)


def builder(func):
    builders[func.__name__] = func
    return func


@builder
def fulltext(conditions):
    value = conditions['fulltext']
    return dict(query_string=dict(query=value))


@builder
def from_(conditions):
    filters = dict()
    if 'from_' in conditions:
        filters['gte'] = conditions['from_'].isoformat()
    if 'until' in conditions:
        filters['lte'] = conditions['until'].isoformat()
    return dict(range={'payload.document.last-semantic-change': filters})


@builder
def until(conditions):
    if 'from_' not in conditions:
        return from_(conditions)


field_map = dict(
    authors='payload.document.author',
)


def query(volume=None,
          year=None,
          topic=None,
          keywords=None,
          raw_tags=None,
          published=None,
          types=(),
          product_id=None,
          serie=None,
          show_news=None,
          filter_terms=None, **kw):
    """ Create elasticsearch query for search. Supported field are:

    fulltext - fulltext to search for
    from_ - search only after from_ datetime. If None, no start to range.
    until - search only until until_ datetime. If None, no end to range.
    volume - volume in which to search. If None, no restriction.
    year - year in which to search (related to volume). If None,
           no restriction.
    topic - the topic to look for. If None, no topic restriction.
    authors - parts of the author's name to look for, whitespace separated.
              If None, no author restriction.
    keywords - keywords to look for, whitespace separated.
              If None, no keyword restriction.
    raw_tags - whole raw-tags content as escaped xml data.
    published - Publication status to look for. If None, no restriction.
    types - a list of document types to look for. If None types don't matter.
    show_news - Display ticker messages or not (boolean)
    filter_terms - an optional list of extra terms to add to the filter.
                   If None, no extra terms.

    Returns elasticsearch query expression that can be passed to `search`.
    """
    clauses = []
    for field, value in kw.items():
        if value is None:
            continue
        elif field in builders:
            clause = builders[field](kw)
            if clause is not None:
                clauses.append(clause)
        elif field in field_map:
            clauses.append(dict(match={field_map[field]: value}))
    if len(clauses) > 1:
        qry = dict(bool=dict(must=clauses))
    elif len(clauses) == 1:
        qry = clauses[0]
    else:
        raise ValueError('no search clauses given')
    return dict(query=qry)
