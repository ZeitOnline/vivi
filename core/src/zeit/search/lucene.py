# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Support for lucene search."""

import logging
import urllib
import urllib2
import xml.sax.saxutils

import gocept.lxml.objectify

import zope.interface

import zeit.search.interfaces
import zeit.search.search


logger = logging.getLogger(__name__)


class LuceneSearch(object):

    zope.interface.implements(zeit.search.interfaces.ISearchInterface)

    index_map = {
        'text': None,  # no transform
        'author': 'autor',
        'volume': 'ausgabe',
        'year': 'jahr',
        'ressort': 'print-ressort',
        'navigation': 'ressort',
        # 'page': 
        # 'serie': 
        # edited
        # correced
        # images_added
    }

    indexes = frozenset(index_map.keys())

    def __call__(self, search_terms):
        logger.info("Lucene search for %s" % search_terms)
        query = self.get_query_args(search_terms)
        tree = self.get_tree(query)
        logger.debug("Lucene search done for %s" % search_terms)
        return set(self.get_result(tree))

    def get_query_args(self, search_terms):
        terms = search_terms.copy()
        text = terms.pop('text', None)
        sort = terms.pop('sort', 'date')

        query = []
        if text:
            query.append(text)

        for key, value in sorted(terms.items()):
            index = self.index_map.get(key)
            if index is None:
                continue
            value = unicode(value)
            query.append('%s:%s' % (
                index, xml.sax.saxutils.quoteattr(value)))

        query = ' '.join(query)

        return urllib.urlencode((
            ('q', query),
            ('sort', sort),
            ('fields', 'author:title'),
            ('res', '100'),
        ))

    def get_tree(self, query):
        base_url = zope.app.appsetup.product.getProductConfiguration(
            'zeit.search').get('lucene-url')
        url = '%s?%s' % (base_url, query)
        logger.debug('Searching Lucene %s' % url)
        request = urllib2.urlopen(url)
        tree = gocept.lxml.objectify.fromfile(request)
        return tree

    def get_result(self, tree):
        try:
            result = tree['page']['result']
        except AttributeError:
            return
        relevance = len(result)
        for node in result:
            unique_id = node.get('url')
            result = zeit.search.search.SearchResult(unique_id)

            result.year = zeit.search.search.make_int(node.get('year'))
            result.volume = zeit.search.search.make_int(node.get('volume'))
            result.title = zeit.search.search.make_unicode(node.find('title'))
            result.author = zeit.search.search.make_unicode(
                node.find('author'))
            result.relevance = relevance
            relevance -= 1
            yield result
