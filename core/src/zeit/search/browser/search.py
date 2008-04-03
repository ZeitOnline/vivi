# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import operator

import zope.cachedescriptors.property
import zope.component
import zope.session.interfaces
import zope.viewlet.viewlet

import zope.app.publisher.browser.directoryresource

import zc.table.table

import zeit.cms.browser.listing
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.search.interfaces


class Viewlet(zope.viewlet.viewlet.ViewletBase):

    states = (
        dict(index='corrected',
             title=_('status-corrected')),
        dict(index='images_added',
             title=_('status-images-added')),
    )

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
        return zope.session.interfaces.ISession(self.request)[
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
        text = ' '.join(
            unicode(s)
            for s in [item.title, item.author, item.year, item.volume,
                      item.page]
            if s)

        return ('<span class="SearchableText">%s</span>'
                '<span class="URL">%s</span>' % (
                    text, url))


class Search(object):

    title = _('Search')
    prefix = 'search.'
    no_content_message = _('The search had no results.')

    @zope.cachedescriptors.property.Lazy
    def columns(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        base_url = zope.component.getMultiAdapter(
            (repository, self.request),
            name='absolute_url')()

        return (
            zeit.cms.browser.listing.GetterColumn(
                _('Author'),
                lambda t, c: t.author),
            zeit.cms.browser.listing.GetterColumn(
                _('Title'),
                lambda t, c: t.title),
            zeit.cms.browser.listing.GetterColumn(
                _('Year/Vol.'),
                lambda t, c: '%s / %s' % (t.year, t.volume),
                name='year_volume'),
            zeit.cms.browser.listing.GetterColumn(
                _('Page'),
                lambda t, c: t.page),
            MetadataColumn(base_url, name='metadata'),
        )


    def update(self):
        self.save_search_terms()

    @zope.cachedescriptors.property.Lazy
    def content(self):
        return self.search(self.munge(self.last_search))

    def munge(self, search_args):
        search_args = search_args.copy()
        if 'state' in search_args:
            # TODO this needs testing!
            search_state = search_args.pop('state')
            pre_cond = []
            # XXX This is very handcrafted and ugly
            preconditions = {
                'corrected': ('edited',),
                'images_added': ('edited', )
            }

            for state in preconditions.get(search_state, []):
                search_args[state] = ('yes', 'notnecessary')
            search_args[search_state] = 'no'

        return search_args

    @zope.cachedescriptors.property.Lazy
    def contentTable(self):
        """Returns table listing contents"""
        formatter = zc.table.table.FormFullFormatter(
            self.context, self.request, self.content,
            columns=self.columns, prefix='search-table')
        formatter.cssClasses['table'] = 'contentListing hasMetadata'
        return formatter

    @property
    def last_search_hidden_fields(self):
        session = zope.session.interfaces.ISession(self.request)[
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
        session = zope.session.interfaces.ISession(self.request)[
            'zeit.search']
        return session['last_search']

    def save_search_terms(self):
        data = self.request.form
        if not data:
            return
        search = dict((key[len(self.prefix):], value)
                      for key, value in data.items()
                      if key.startswith(self.prefix))
        session = zope.session.interfaces.ISession(self.request)[
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
