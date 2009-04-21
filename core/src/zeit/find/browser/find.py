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


class SearchForm(zeit.cms.browser.view.Base):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/json')
        r = resources(self.request)
        result = {"template_url": r['search_form.jsont']()}
        return cjson.encode(result)


class SearchResult(zeit.cms.browser.view.Base):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/json')
        r = resources(self.request)
        self.arrow_right_url = r['arrow_right.png']()
        result = {
            "template_url": r['search_result.jsont'](),
            "results":
                [{'uniqueId': 'foo',
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
                 {'uniqueId': 'bar',
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
                  'topics': 'Newspapers',
                  'topics_filter': '',
                  'author': 'Christian Zagrodnick',
                  'author_filter': ''}]
                 }
        return cjson.encode(result)
