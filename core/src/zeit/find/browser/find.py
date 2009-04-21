# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.cms.browser.view
import zc.resourcelibrary
import zope.component
import zope.interface


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
    
    def json(self):
        r = self.resources
        return {
            "results":
                [{'uniqueId': 'http://xml.zeit.de/online/2007/01/Somalia',
                  'icon': 'http://localhost:8080/@@/zeit-content-article-interfaces-IArticle-zmi_icon.png',
                  'favorited': r['favorite.png'](),
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
                  'author_filter': ''},
                 {'uniqueId': 'http://xml.zeit.de/online/2007/01/eta-zapatero',
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
                  'author_filter': ''}]
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
                     {"title": "Ressorts", "entries": self.topic_entries()}]},
            {"row": [{"title": "Autoren", "entries": self.author_entries()},
                     {"title": "Inhaltstyp", "entries": self.content_types_entries()}]}]}
