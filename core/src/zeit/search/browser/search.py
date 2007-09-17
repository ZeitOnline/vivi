# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import operator

import zope.cachedescriptors.property
import zope.component
import zope.viewlet.viewlet

import zope.app.session.interfaces

import zeit.connector.search
import zeit.cms.interfaces


class Viewlet(zope.viewlet.viewlet.ViewletBase):

    @zope.cachedescriptors.property.Lazy
    def ressorts(self):
        # XXX where to get the data from? bug #3751
        return ['wirtschaft', 'politik']

    @property
    def last_search(self):
        return zope.app.session.interfaces.ISession(self.request)[
        'zeit.search'].get('last_search', {})


class SearchResult(object):

    def __init__(self, name, unique_id, author, year):
        self.__name__ = name
        self.unique_id = unique_id  # XXX
        self.author = author
        self.year = year



class Search(zeit.cms.browser.listing.Listing):

    title = 'Suche'
    enalbe_delete = False

    _search_map = {
        'author': zeit.connector.search.SearchVar(
            'author', 'http://namespaces.zeit.de/document/'),
        'ressort': zeit.connector.search.SearchVar(
            'ressort', 'http://namespaces.zeit.de/document/'),
        'volume': zeit.connector.search.SearchVar(
            'volume', 'http://namespaces.zeit.de/document/'),
        'year': zeit.connector.search.SearchVar(
            'year', 'http://namespaces.zeit.de/document/'),
    }

    def __call__(self):
        self.save_search_terms()
        return self.index()

    def get_search_term(self):
        terms = []
        for field, var in self._search_map.items():
            value = self.request.get(field)
            if not value:
                continue
            terms.append(var == value)
        if not terms:
            return None
        return reduce(operator.and_, terms)

    @zope.cachedescriptors.property.Lazy
    def content(self):
        term = self.get_search_term()
        if term is None:
            return []
        var = self._search_map.get
        search_result = self.connector.search(
            [var('author'), var('year')], term)
        return [SearchResult(*r) for r in search_result]


    def save_search_terms(self):
        data = self.request.form
        if not data:
            return
        session = zope.app.session.interfaces.ISession(self.request)[
            'zeit.search']
        session['last_search'] = data

    @zope.cachedescriptors.property.Lazy
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)
