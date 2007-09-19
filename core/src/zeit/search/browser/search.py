# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import operator

import zope.cachedescriptors.property
import zope.component
import zope.viewlet.viewlet

import zope.app.session.interfaces
import zope.app.publisher.browser.directoryresource

import z3c.zrtresource.zrtresource
import zc.table.table

import zeit.cms.browser.listing
import zeit.cms.interfaces
import zeit.cms.repository.interfaces

import zeit.search.interfaces


(zope.app.publisher.browser.directoryresource.
 DirectoryResource.resource_factories['.js']) = (
     z3c.zrtresource.zrtresource.ZRTFileResourceFactory)


class Viewlet(zope.viewlet.viewlet.ViewletBase):

    @zope.cachedescriptors.property.Lazy
    def print_ressorts(self):
        return zeit.cms.content.sources.PrintRessortSource()

    @zope.cachedescriptors.property.Lazy
    def navigations(self):
        return zeit.cms.content.sources.NavigationSource()

    @zope.cachedescriptors.property.Lazy
    def serien(self):
        return zeit.cms.content.sources.SerieSource()

    @property
    def last_search(self):
        return zope.app.session.interfaces.ISession(self.request)[
            'zeit.search'].get('last_search', {})

    @property
    def form_class(self):
        return (self.preferences.show_extended
                and 'show-extended' or 'hide-extended' )

    @zope.cachedescriptors.property.Lazy
    def preferences(self):
        return zope.app.preference.interfaces.IUserPreferences(
            self.context).search_preferences


class MetadataColumn(zc.table.column.GetterColumn):

    def __init__(self, base_url, **kwargs):
        if not base_url.endswith('/'):
            base_url = base_url + '/'
        self.base_url = base_url
        super(MetadataColumn, self).__init__(**kwargs)

    def getter(self, item, formatter):
        url = item.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE,
                                    self.base_url)
        return ('<span class="SearchableText">%s</span>'
                '<span class="URL">%s</span>' % (
                    'XXX', url))


class Search(object):

    title = 'Suche'
    prefix = 'search.'

    @zope.cachedescriptors.property.Lazy
    def columns(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        base_url = zope.component.getMultiAdapter(
            (repository, self.request),
            name='absolute_url')()

        return (
            zeit.cms.browser.listing.GetterColumn(
                u'Autor',
                lambda t, c: t.author),
            zeit.cms.browser.listing.GetterColumn(
                u'Titel',
                lambda t, c: t.title),
            zeit.cms.browser.listing.GetterColumn(
                u'Jahr/Vol.',
                lambda t, c: '%s / %s' % (t.year, t.volume),
                name='year_volume'),
            zeit.cms.browser.listing.GetterColumn(
                u'Seite',
                lambda t, c: t.page),
            MetadataColumn(base_url, name='metadata'),
        )


    def __call__(self):
        self.save_search_terms()
        return self.index()

    @zope.cachedescriptors.property.Lazy
    def content(self):
        return self.search(self.last_search)

    @zope.cachedescriptors.property.Lazy
    def contentTable(self):
        """Returns table listing contents"""
        formatter = zc.table.table.FormFullFormatter(
            self.context, self.request, self.content,
            columns=self.columns, prefix='search-table')
        formatter.cssClasses['table'] = 'contentListing'
        return formatter

    @property
    def last_search_hidden_fields(self):
        session = zope.app.session.interfaces.ISession(self.request)[
            'zeit.search']
        last_search = session.get('last_search')
        for key, value in last_search.items():
            if isinstance(value, int):
                name = '%s:int' % key
            else:
                name = key
            name = '%s%s' % (self.prefix, name)
            yield dict(name=name, value=value)

    @property
    def last_search(self):
        session = zope.app.session.interfaces.ISession(self.request)[
            'zeit.search']
        return session['last_search']

    def save_search_terms(self):
        data = self.request.form
        if not data:
            return
        search = dict((key[len(self.prefix):], value)
                      for key, value in data.items()
                      if key.startswith(self.prefix))
        session = zope.app.session.interfaces.ISession(self.request)[
            'zeit.search']
        session['last_search'] = search

    def toggle_extended_search(self):
        self.preferences.show_extended = not self.preferences.show_extended

    @zope.cachedescriptors.property.Lazy
    def preferences(self):
        return zope.app.preference.interfaces.IUserPreferences(
            self.context).search_preferences

    @zope.cachedescriptors.property.Lazy
    def search(self):
        return zope.component.getUtility(zeit.search.interfaces.ISearch)
