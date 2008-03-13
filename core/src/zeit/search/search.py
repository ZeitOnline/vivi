# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import operator
import urllib
import urllib2

import zope.component
import zope.interface

import gocept.lxml.objectify

import zeit.cms.interfaces
import zeit.cms.browser.interfaces
import zeit.connector.search

import zeit.search.interfaces


logger = logging.getLogger('zeit.search')


# helper functions

def make_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def make_unicode(value):
    if value is None:
        return None
    return unicode(value)


class SearchResult(object):
    """Represents one item in a list of results."""

    zope.interface.implements(zeit.search.interfaces.ISearchResult)

    title = None
    author = None

    year = None
    volume = None
    page = None

    relevance = 0

    def __init__(self, unique_id, weight=0):
        self.uniqueId = unique_id
        self.__name__ = unique_id.rsplit('/', 1)[1]
        self.weight = weight

    def updated_by(self, other):
        target = SearchResult(self.uniqueId)
        sources = sorted([self, other], key=lambda x: x.weight, reverse=True)
        for attr_name in ('title', 'author', 'year', 'volume', 'page'):
            for source in sources:
                value = getattr(source, attr_name, None)
                if value is not None:
                    break
            setattr(target, attr_name, value)
        target.relevance = max(self.relevance, other.relevance)
        return target


class MetaSearch(object):

    zope.interface.implements(zeit.search.interfaces.ISearch)

    def __call__(self, search_terms):

        # filter out empty terms
        search_terms = dict((key, value)
                            for key, value in search_terms.items()
                            if value)

        search_interfaces = zope.component.getUtilitiesFor(
            zeit.search.interfaces.ISearchInterface)
        results = []
        search_indexes = set(search_terms.keys())

        # Gather data
        for name, search in search_interfaces:
            if not search.indexes & search_indexes:
                # Nothing to search at this interface
                continue
            results.append(search(search_terms))

        if not results:
            # shortcut for no results, code below relies on having at least one
            # result. Note that this only happens when *no* search interface is
            # registered.
            return frozenset()

        # Create dictionaries of the search results for looking up the results
        # by unique id
        result_dicts = []
        for result in results:
            result_dicts.append(
                dict((item.uniqueId, item) for item in result))

        # Intersect the dict keys (i.e. unique ids) to create the set unique
        # ids which are contained in the result
        result_ids = reduce(
            operator.and_, (set(result.keys()) for result in result_dicts))

        # Create the final result set and merge the metadata according to the
        # weight
        search_result = []
        for result_id in result_ids:
            search_result.append(
                reduce(lambda a, b: a.updated_by(b),
                       (result[result_id] for result in result_dicts)))

        return sorted(search_result, key=lambda x: x.relevance, reverse=True)


class XapianSearch(object):
    """Interface to Zeit Xapian."""

    zope.interface.implements(zeit.search.interfaces.ISearchInterface)

    indexes = frozenset(['text'])

    def __call__(self, search_terms):
        if 'text' not in search_terms:
            return set()
        text = search_terms['text']
        logger.info('Xapian search for: %r' % text)
        tree = self.get_tree(text)
        logger.debug('Xapian search done.')
        return set(self.get_result(tree))

    def get_tree(self, text):
        base_url = zope.app.appsetup.product.getProductConfiguration(
            'zeit.search').get('xapian-url')
        query = dict(q=text, op='AND', ps=100)
        url = '%s?%s' % (base_url, urllib.urlencode(query))
        request = urllib2.urlopen(url)
        return gocept.lxml.objectify.fromfile(request)

    def get_result(self, tree):
        try:
            result = tree.page.result
        except AttributeError:
            return
        relevance = len(result)
        for node in result:
            unique_id = node.get('url').replace(
                'http://www.zeit.de/', zeit.cms.interfaces.ID_NAMESPACE)
            result = SearchResult(unique_id)

            result.year = make_int(node.get('year'))
            result.volume = make_int(node.get('volume'))
            result.title = make_unicode(node.title)
            result.author = make_unicode(node.author)
            result.relevance = relevance
            relevance -= 1
            yield result


class MetadataSearch(object):
    """Zeit metadata search via connector."""

    zope.interface.implements(zeit.search.interfaces.ISearchInterface)

    ns = 'http://namespaces.zeit.de/CMS/document'
    qps = 'http://namespaces.zeit.de/QPS/attributes'
    _search_map = {
        'author': zeit.connector.search.SearchVar('author', ns),
        'ressort': zeit.connector.search.SearchVar('ressort', ns),
        'volume': zeit.connector.search.SearchVar('volume', ns),
        'year': zeit.connector.search.SearchVar('year', ns),
        'title': zeit.connector.search.SearchVar('title', ns),
        'serie': zeit.connector.search.SearchVar('serie', ns),

        'page': zeit.connector.search.SearchVar('page', qps),
        'print_ressort': zeit.connector.search.SearchVar('ressort', qps),
    }

    indexes = frozenset(_search_map.keys())

    def __call__(self, search_terms):
        term = self.get_search_term(search_terms)
        if term is None:
            return set()
        logger.info('Metadata search for: %r' % search_terms)
        result = self.get_result(term)
        logger.debug('Metadata search done.')
        return set(result)

    def get_result(self, term):
        var = self._search_map.get
        search_result = self.connector.search(
            [var('author'), var('volume'),
             var('year'), var('page'), var('title')],
            term)

        for unique_id, author, volume, year, page, title in search_result:
            # Metadata search result is rated higher because it is the freshest
            #  data we've got
            result = SearchResult(unique_id, weight=1)
            result.author = make_unicode(author)
            result.title = make_unicode(title)
            result.year = make_int(year)
            result.volume = make_int(volume)
            result.page = make_int(page)
            yield result

    def get_search_term(self, search):
        terms = []
        for field, var in self._search_map.items():
            value = search.get(field)
            if not value:
                continue
            terms.append(var == unicode(value))
        if not terms:
            return None
        return reduce(operator.and_, terms)

    @property
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)


class ZeitSearch(XapianSearch):
    """Zeit fulltext search via public interface."""

    zope.interface.implements(zeit.search.interfaces.ISearchInterface)

    index_prefixes = {
        'text': '',
        'year': 'jahr:',
        'volume': 'ausgabe:',
        'navigation': 'rubrik:',
    }

    def __call__(self, search_terms):
        assert 'text' in search_terms
        base_url = zope.app.appsetup.product.getProductConfiguration(
            'zeit.search').get('dwds-url')
        url = '%s?%s' % (base_url, self.get_query(search_terms))
        logger.info('Searching DWDS %s' % url)
        request = urllib2.urlopen(url)
        tree = gocept.lxml.objectify.fromfile(request)
        return self.get_result(tree)

    def get_query(self, search_terms):
        index_query = []
        for key, value in search_terms.items():
            prefix = self.index_prefixes.get(key)
            if prefix is None:
                continue
            index_query.append(
                (u'%s%s' % (prefix, value)).encode('utf8'))

        sort = search_terms.get('sort', 'aktuell')

        return urllib.urlencode(dict(
            q=' AND '.join(index_query),
            out='xml',
            ps='100',
            sort=sort))

    def get_result(self, tree):
        url_trash = '/home/ddc/ZEIT_CMS/'
        for result in super(ZeitSearch, self).get_result(tree):
            if result.uniqueId.startswith(url_trash):
                result.uniqueId = result.uniqueId.replace(url_trash, '', 1)
            yield result
