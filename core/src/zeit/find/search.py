# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.solr import query as lq
from zeit.find.daterange import DATE_FILTERS
import itertools
import zeit.solr.interfaces
import zope.component


def search(q, sort_order=None):
    """Search solr according to query.

    q - the lucene query
    sort_order - sort by either either 'relevance' or 'date'.

    Returns the pysolr Result object.
    """
    if q is None:
        return []

    if q == lq.any_value():
        sort_order = 'date'
    else:
        sort_order = sort_order or 'relevance'
    if sort_order == 'relevance':
        sort_order = 'score desc'
    elif sort_order == 'date':
        sort_order = 'last-semantic-change desc'

    result_fields = [
        'authors',
        'graphical-preview-url',
        'icon',
        'keywords',
        'raw-tags',
        'last-semantic-change',
        'published',
        'range',
        'range_details',
        'ressort',
        'serie',
        'subtitle',
        'supertitle',
        'teaser_text',
        'teaser_title',
        'title',
        'uniqueId',
        'volume',
        'year',
    ]

    conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    return conn.search(q, sort=sort_order, fl=' '.join(result_fields),
                       rows=50)


def counts(q):
    """Count in solr according to query.

    q - the lucene query

    Returns tuple of time counts, topic counts, author counts, type counts.

    Each counts is a list of (name, count) tuples. Counts of zero are
    not returned.
    """
    date_filters = DATE_FILTERS()
    date_queries = [filter for (name, filter) in date_filters]

    facets = {
        'facet': 'true',
        'facet.field': ['ressort', 'type', 'authors'],
        'facet.mincount': 1,
        'facet.query': date_queries,
        }

    conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    facet_data = conn.search(q, rows=0, **facets).facets

    facet_queries = facet_data['facet_queries']
    time_counts = []
    for name, filter in date_filters:
        time_counts.append((name, facet_queries[filter]))

    facet_fields = facet_data['facet_fields']

    _counts = lambda counts: sorted(grouper(2, counts))

    topic_counts = _counts(facet_fields['ressort'])
    author_counts = _counts(facet_fields['authors'])
    type_counts = _counts(facet_fields['type'])

    return time_counts, topic_counts, author_counts, type_counts


def query(fulltext=None,
          from_=None,
          until=None,
          volume=None,
          year=None,
          topic=None,
          authors=None,
          keywords=None,
          raw_tags=None,
          published=None,
          types=(),
          product_id=None,
          serie=None,
          show_news=None,
          filter_terms=None):
    """Create lucene query string for search.

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
    Returns lucene query string that can be passed to solr.
    """
    filter_terms = filter_terms or []

    terms = []
    if fulltext:
        terms.append(lq.field_raw('text', fulltext))
    if from_ is not None or until is not None:
        terms.append(
            lq.datetime_range('last-semantic-change', from_, until))
    if volume is not None:
        terms.append(
            lq.field('volume', volume))
    if year is not None:
        terms.append(
            lq.field('year', year))
    if topic is not None:
        terms.append(lq.field('ressort', topic))
    if authors is not None:
        terms.append(lq.multi_field('authors_fulltext', authors))
    if keywords is not None:
        terms.append(lq.multi_field('keywords', keywords))
    if raw_tags is not None:
        terms.append(lq.multi_field('raw-tags', raw_tags))
    if published is not None:
        terms.append(lq.field('published', published))
    type_terms = []
    for type in types:
        type_terms.append(lq.field('type', type))
    if type_terms:
        terms.append(lq.or_(*type_terms))
    if product_id is not None:
        terms.append(lq.field('product_id', product_id))
    if serie is not None:
        terms.append(lq.field('serie', serie))
    if not show_news:
        terms.append(lq.not_(lq.field('ressort', 'News')))
        terms.append(lq.not_(lq.field('product_text', 'News')))

    terms.extend(filter_terms)
    if terms:
        return lq.and_(*terms)
    return lq.any_value()


def grouper(n, iterable, padvalue=None):
    return itertools.izip(
        *[itertools.chain(iterable, itertools.repeat(padvalue, n-1))]*n)
