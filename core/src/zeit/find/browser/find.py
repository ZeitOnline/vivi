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

    def template_url(self):
        if self.template is None:
            return None
        return self.resources[self.template]()


class SearchForm(JSONView):
    template = 'search_form.jsont'


class SearchResult(JSONView):
    template = 'search_result.jsont'

    def url(self, view, uniqueId):
        return super(SearchResult, self).url(
            self.context, '%s?uniqueId=%s' % (view, uniqueId))

    def json(self):
        r = self.resources
        somalia_id = 'http://xml.zeit.de/online/2007/01/Somalia'
        zapatero_id = 'http://xml.zeit.de/online/2007/01/eta-zapatero'
        return {
            "results":
                [{'uniqueId': somalia_id,
                  'icon': 'http://localhost:8080/@@/zeit-content-article-interfaces-IArticle-zmi_icon.png',
                  'favorited': r['not_favorite.png'](),
                  'publication_status': r['published.png'](),
                  'arrow': r['arrow_right.png'](),
                  'teaser_title': 'Obama still alive',
                  'teaser_text': 'Obama is still alive and well.',
                  'preview_url': '',
                  'date': '13.02.2009',
                  'date_filter': '',
                  'week': '13/2009',
                  'week_filter': '',
                  'topics': 'Politik',
                  'topics_filter': '',
                  'author': 'Martijn Faassen',
                  'author_filter': '',
                  'related_url': self.url(
                      'expanded_search_result', somalia_id),
                  'favorite_url': self.url('toggle_favorited', somalia_id),
                  },
                 {'uniqueId': zapatero_id,
                  'icon': 'http://localhost:8080/@@/zeit-content-article-interfaces-IArticle-zmi_icon.png',
                  'favorited': r['not_favorite.png'](),
                  'publication_status': r['unpublished.png'](),
                  'arrow': r['arrow_right.png'](),
                  'teaser_title': 'Obama journalism too extreme',
                  'teaser_text': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et',
                  'preview_url': '',
                  'date': '19.02.2009',
                  'date_filter': '',
                  'week': '14/2009',
                  'week_filter': '',
                  'topics': 'Kultur',
                  'topics_filter': '',
                  'author': 'Christian Zagrodnick',
                  'author_filter': '',
                  'related_url': self.url(
                      'expanded_search_result', zapatero_id),
                  'favorite_url': self.url('toggle_favorited', zapatero_id),
                  },
                 ]
            }


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

    clip_id = u'Favoriten'

    def json(self):
        r = self.resources
        uid = self.request.get('uniqueId')
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(
            self.request.principal)
        content = zeit.cms.interfaces.ICMSContent(uid)

        if not self.clip_id in clipboard.keys():
            clipboard.addClip(self.clip_id)
        favorites = clipboard[self.clip_id]

        if content.__name__ in favorites.keys():
            del favorites[content.__name__]
            return {'favorited': r['not_favorite.png']()}
        favorites[content.__name__] = (zeit.cms.clipboard.
                                       interfaces.IClipboardEntry(content))
        return {'favorited': r['favorite.png']()}
