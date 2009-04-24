# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.cms.browser.view
import zc.resourcelibrary
import zope.component
import zope.interface
import zeit.cms.interfaces
import zeit.cms.clipboard.interfaces
import zeit.cms.browser.interfaces


def resources(request):
    return zope.component.getAdapter(
        request, zope.interface.Interface, name='zeit.find')


class Find(zeit.cms.browser.view.Base):

    def __call__(self):
        zc.resourcelibrary.need('zeit.find')
        return super(Find, self).__call__()


class JSONView(zeit.cms.browser.view.Base):
    template = None

    def __init__(self, context, request):
        super(JSONView, self).__init__(context, request)
        self.resources = resources(request)

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/json')
        result = self.json()
        url = self.template_url()
        if url is not None:
            result['template_url'] = url
        return cjson.encode(result)

    def json(self):
        return {}

    @property
    def favorites(self):
        favorites_id = u'Favoriten'

        clipboard = zeit.cms.clipboard.interfaces.IClipboard(
            self.request.principal)
        if not favorites_id in clipboard.keys():
            clipboard.addClip(favorites_id)
        return clipboard[favorites_id]

    def url(self, view, uniqueId):
        return super(JSONView, self).url(
            self.context, '%s?uniqueId=%s' % (view, uniqueId))

    def template_url(self):
        if self.template is None:
            return None
        return self.resources[self.template]()

    def result_entry(self, article):
        r = self.resources
        uid = article.uniqueId
        listrepr = zope.component.queryMultiAdapter(
            (article, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)
        if article.__name__ in self.favorites.keys():
            favorited_icon = r['favorite.png']()
        else:
            favorited_icon = r['not_favorite.png']()
        return {
            'uniqueId': uid,
            'icon': 'http://localhost:8080/@@/zeit-content-article-interfaces-IArticle-zmi_icon.png',
            'favorited': favorited_icon,
            'publication_status': r['published.png'](),
            'arrow': r['arrow_right.png'](),
            'teaser_title': listrepr.title,
            'teaser_text': listrepr.searchableText,
            'preview_url': '',
            'date': '13.02.2009',
            'date_filter': '',
            'week': '13/2009',
            'week_filter': '',
            'topics': 'Politik',
            'topics_filter': '',
            'author': listrepr.author,
            'author_filter': '',
            'related_url': self.url('expanded_search_result', uid),
            'favorite_url': self.url('toggle_favorited', uid),
        }


class SearchForm(JSONView):
    template = 'search_form.jsont'


class SearchResult(JSONView):
    template = 'search_result.jsont'

    def json(self):
        if self.request.get('fulltext', '') == '':
            return {"results": []}
        articles = ['4schanzentournee-abgesang',
                    'elterngeld-schlieben',
                    'EU-Beitritt-rumaenien-bulgarien',
                    'Somalia',
                    'eta-zapatero']
        return {
            "results": [
                self.result_entry(zeit.cms.interfaces.ICMSContent(uid))
                for uid in [
                    'http://xml.zeit.de/online/2007/01/%s' % id_
                    for id_ in articles]]}


class ExtendedSearchForm(JSONView):
    template = 'extended_search_form.jsont'


class ResultFilters(JSONView):
    template = 'result_filters.jsont'

    def time_entries(self):
        return [{"title": "heute", "amount": "20", "query": ""},
                {"title": "7 Tage", "amount": "1000+", "query": ""}]

    def author_entries(self):
        return [{"title": "Martijn Faassen", "amount": "45", "query": ""},
                {"title": "Christian Zagrodnick", "amount": "124", "query": ""}]

    def topic_entries(self):
        return [{"title": "Politik", "amount": "10", "query": ""},
                {"title": "Kultur", "amount": "7", "query": ""},
                {"title": "Kultur", "amount": "7", "query": ""}]

    def content_types_entries(self):
        return [ {"title": "Artikel", "amount": "1000+", "query": ""}]

    def json(self):
        return {"results": [
            {"row": [{"title": "Zeit", "entries": self.time_entries()},
                     {"title": "Ressort", "entries": self.topic_entries()}]},
            {"row": [{"title": "Autor", "entries": self.author_entries()},
                     {"title": "Inhaltstyp", "entries": self.content_types_entries()}]}]}


class ExpandedSearchResult(JSONView):
    template = 'expanded_search_result.jsont'

    def json(self):
        r = self.resources
        return {
            'results': [
                {'uniqueId': 'http://xml.zeit.de/online/2007/01/Somalia',
                 'publication_status': r['published.png'](),
                 'short_teaser_title': 'Obama is a cat?',
                 'short_teaser_text': 'Obama speculated to be a feline',
                 },
                {'uniqueId': 'http://xml.zeit.de/online/2007/01/eta-zapatero',
                 'publication_status': r['unpublished.png'](),
                 'short_teaser_title': "Obama or O'Bama?",
                 'short_teaser_text': "Evidence suggests Obama is Irish",
                 },
                ],
            }


class ToggleFavorited(JSONView):
    template = 'toggle_favorited.jsont'

    def json(self):
        r = self.resources
        content = zeit.cms.interfaces.ICMSContent(
            self.request.get('uniqueId'))

        if content.__name__ in self.favorites.keys():
            del self.favorites[content.__name__]
            return {'favorited': r['not_favorite.png']()}
        self.favorites[content.__name__] = (zeit.cms.clipboard.
                                       interfaces.IClipboardEntry(content))
        return {'favorited': r['favorite.png']()}


class Favorites(JSONView):
    template = 'search_result.jsont'

    def json(self):
        return {"results": [
            self.result_entry(a) for a in [
                zeit.cms.interfaces.ICMSContent(c.referenced_unique_id)
                for c in self.favorites.values()]]}
