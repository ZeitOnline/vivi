from zeit.find.interfaces import ICMSSearch
from zope.app.appsetup.product import getProductConfiguration
from zope.interface import implementer
import zeit.retresco.search


DEFAULT_FIELDS = (
    'url',
    'doc_type',
    'doc_id',
    'payload',
    'title',
    'teaser',
)


class Elasticsearch(zeit.retresco.search.Elasticsearch):

    def search(self, query, **kw):
        query.setdefault('_source', DEFAULT_FIELDS)
        kw.setdefault('rows', 50)
        return super().search(query, **kw)


@implementer(ICMSSearch)
def from_product_config():
    """Get the utility configured with data from the product config."""
    config = getProductConfiguration('zeit.find')
    return Elasticsearch(config['elasticsearch-url'],
                         config['elasticsearch-index'])


field_map = dict(
    authors='payload.document.author',
    author_type='payload.xml.status',
    access='payload.document.access',
    product_id='payload.workflow.product-id',
    published='payload.vivi.publish_status',
    raw_tags='body',
    serie='payload.document.serie',
    topic='payload.document.ressort',
    types='doc_type',
    volume='payload.document.volume',
    year='payload.document.year',
)


rtr_fields = (
    'rtr_events',
    'rtr_keywords',
    'rtr_locations',
    'rtr_organisations',
    'rtr_persons',
    'rtr_products',
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
    filters = []
    clauses = dict()
    # handle fulltext
    if fulltext:
        must.append(dict(query_string=dict(
            query=fulltext, default_operator='AND')))
    # handle from_, until
    from_ = conditions.pop('from_', None)
    until = conditions.pop('until', None)
    if from_ is not None or until is not None:
        filters.append(dict(range={
            'payload.document.last-semantic-change':
            zeit.retresco.search.date_range(from_, until)}))
    # handle show_news
    if not conditions.pop('show_news', True):
        clauses['must_not'] = [
            dict(match={'payload.document.ressort': 'News'})] + [
                dict(match={'payload.workflow.product-id': pid})
                for pid in ('News', 'afp', 'SID', 'dpa-hamburg')]
    # handle "keywords" (by querying all `rtr_*` fields)
    keyword = conditions.pop('keywords', None)
    if keyword is not None:
        filters.append(dict(bool=dict(should=[
            dict(match={field: keyword}) for field in rtr_fields])))
    # handle autocomplete queries as prefix matches
    autocomplete = conditions.pop('autocomplete', None)
    if autocomplete is not None:
        # payload.teaser.title is copied and lowercased to
        # payload.vivi.autocomplete by the ES mapping, so this hopefully should
        # be somewhat generically applicable (even though we currently only use
        # it for IAuthor objects).
        must.append(dict(match_phrase_prefix={
            'payload.vivi.autocomplete': autocomplete}))
    # handle remaining fields
    for field, value in conditions.items():
        if value in (None, [], ()):
            continue
        elif field not in field_map:
            raise ValueError('unsupported search condition {}', field)
        elif isinstance(value, (list, tuple)):
            filters.append(dict(bool=dict(should=[
                dict(match={field_map[field]: v}) for v in value])))
        else:
            filters.append(dict(match={field_map[field]: value}))
    # construct either bool or simple query
    if must:
        clauses['must'] = must
    if filters:
        clauses['filter'] = filters
    if len(clauses) == 1:
        subclause = list(clauses.values())[0]
        if len(subclause) == 1:
            qry = subclause[0]
        else:
            qry = dict(bool=clauses)
    elif clauses:
        qry = dict(bool=clauses)
    else:
        qry = dict(match_all=dict())
    return dict(query=qry)
