from json import dumps
from logging import getLogger
from zope.component import getUtility
from zeit.retresco.interfaces import IElasticsearch
from zeit.retresco.search import Elasticsearch


log = getLogger(__name__)


default_source = (
    'url',
    'doc_type',
    'doc_id',
    'payload',
    'supertitle',
    'teaser',
    'title',
)


sort_orders = dict(
    date='payload.document.last-semantic-change:desc',
    relevance='_score',
)


class Search(Elasticsearch):

    def __init__(self, searcher):
        self.client = searcher.client
        # TODO: this should be part of the product config
        self.index = 'zeit_pool_content'


def search(query, sort_order=None, additional_result_fields=(), rows=50, **kw):
    """Search elasticsearch according to query."""
    if query is None:
        return []
    query.setdefault('_source', default_source)
    sort_order = sort_orders.get(sort_order)
    elasticsearch = Search(getUtility(IElasticsearch))
    log.debug('searching using query "%s"', dumps(query))
    return elasticsearch.search(query, sort_order=sort_order, rows=rows, **kw)


field_map = dict(
    authors='payload.document.author',
    keywords='rtr_keywords',
    product_id='payload.workflow.product-id',
    published='payload.vivi.publish_status',
    raw_tags='rtr_tags',
    serie='payload.document.serie',
    topic='payload.document.ressort',
    types='doc_type',
    volume='payload.document.volume',
    year='payload.document.year',
)


def query(fulltext=None, **conditions):
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
    must = []
    clauses = dict()
    # handle fulltext
    if fulltext:
        must.append(dict(query_string=dict(query=fulltext)))
    # handle from_, until
    from_ = conditions.pop('from_', None)
    until = conditions.pop('until', None)
    if from_ is not None or until is not None:
        filters = dict()
        if from_ is not None:
            filters['gte'] = from_.isoformat()
        if until is not None:
            filters['lte'] = until.isoformat()
        must.append(dict(range={
            'payload.document.last-semantic-change': filters}))
    # handle show_news
    if not conditions.pop('show_news', True):
        clauses['must_not'] = [
            dict(match={'payload.document.ressort': 'News'})] + [
                dict(match={'payload.workflow.product-id': pid})
                for pid in 'News', 'afp', 'SID', 'dpa-hamburg']
    # handle remaining fields
    for field, value in conditions.items():
        if value in (None, [], ()):
            continue
        elif field not in field_map:
            raise ValueError('unsupported search condition {}', field)
        elif isinstance(value, (list, tuple)):
            must.append(dict(bool=dict(should=[
                dict(match={field_map[field]: v}) for v in value])))
        else:
            must.append(dict(match={field_map[field]: value}))
    # construct either bool or simple query
    if must:
        clauses['must'] = must
    if len(clauses) == 1 and len(clauses.get('must', [])) == 1:
        qry = clauses['must'][0]
    elif clauses:
        qry = dict(bool=clauses)
    else:
        qry = dict(match_all=dict())
    return dict(query=qry)
