# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import itertools
import pysolr
import zope.app.appsetup.product
from zeit.find import lucenequery as lq
from zeit.find.daterange import DATE_FILTERS

TYPES = ['article', 'gallery', 'video', 'teaser', 'centerpage']

def get_solr():
    """Make a connection with Apache Solr.

    Use configuration as specified in zeit.find 'solr_url' field in
    product-specific configuration.
    """
    config = zope.app.appsetup.product.getProductConfiguration('zeit.find')
    solr_url = config.get('solr_url')
    return pysolr.Solr(solr_url)

def search(q, sort_order=None):
    """Search solr according to query.

    q - the lucene query
    sort_order - sort by either either 'relevance' or 'date'.

    Returns the pysolr Result object.
    """
    if q is None:
        return []

    sort_order = sort_order or 'relevance'
    if sort_order == 'relevance':
        sort_order = 'score desc'
    elif sort_order == 'date':
        sort_order = 'last-semantic-change desc'

    result_fields = ['uniqueId', 'published',
                     'teaser_title', 'teaser_text',
                     'last-semantic-change', 'ressort',
                     'authors', 'volume', 'year', 'title', 'icon']

    conn = get_solr()
    return conn.search(q, sort=sort_order, fl=' '.join(result_fields),
                       rows=100)

def counts(q):
    """Count in solr according to query.

    q - the lucene query

    Returns tuple of time counts, topic counts, author counts, type counts.

    Each counts is a list of (name, count) tuples. Counts of zero are
    not returned.
    """
    date_queries = [filter for (name, filter) in DATE_FILTERS]

    facets = {
        'facet': 'true',
        'facet.field': ['ressort', 'type', 'authors'],
        'facet.mincount': 1,
        'facet.query': date_queries,
        }

    conn = get_solr()
    facet_data = conn.search(q, rows=0, **facets).facets

    facet_queries = facet_data['facet_queries']
    time_counts = []
    for name, filter in DATE_FILTERS:
        time_counts.append((name, facet_queries[filter]))

    facet_fields = facet_data['facet_fields']

    _counts = lambda counts: sorted(grouper(2, counts))

    topic_counts = _counts(facet_fields['ressort'])
    author_counts = _counts(facet_fields['authors'])
    type_counts = _counts(facet_fields['type'])

    return time_counts, topic_counts, author_counts, type_counts

def query(fulltext, from_, until, volume, year, topic, authors, keywords,
          published, types, filter_terms=None):
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
    published - Publication status to look for. If None, no restriction.
    types - a list of document types to look for. If None types don't matter.
    filter_terms - an optional list of extra terms to add to the filter.
                   If None, no extra terms.
    Returns lucene query string that can be passed to solr.
    """
    filter_terms = filter_terms or []

    terms = []
    if fulltext:
        terms.append(lq.field('text', fulltext))
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
    if published is not None:
        terms.append(lq.field('published', published))
    type_terms = []
    for type in types:
        type_terms.append(lq.field('type', type))
    if type_terms:
        terms.append(lq.or_(*type_terms))
    else:
        # we find absolutely nothing as there isn't any
        # __neverfound type around
        terms.append(lq.field('type', '__neverfound'))

    terms.extend(filter_terms)
    return lq.and_(*terms)


def grouper(n, iterable, padvalue=None):
    return itertools.izip(
        *[itertools.chain(iterable, itertools.repeat(padvalue, n-1))]*n)
