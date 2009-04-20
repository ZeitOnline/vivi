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
        self.request.response.setHeader('Content-Type', 'text/json')
        result = {
            "template_url": resources(self.request)['result.jsont'](),
            "results":
                [{'uniqueId': 'foo',
                  'icon': 'http://localhost:8080/@@/zeit.find/article.png',
                  'favorited':
                      'http://localhost:8080/@@/zeit.find/favorite.png',
                  'publication_status':
                      'http://localhost:8080/@@/zeit.find/published.png',
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
                  'icon': 'http://localhost:8080/@@/zeit.find/article.png',
                  'favorited':
                      'http://localhost:8080/@@/zeit.find/not_favorit.png',
                  'publication_status':
                      'http://localhost:8080/@@/zeit.find/not_published.png',
                  'teaser_title': 'Obama journalism too extreme',
                  'teaser_text': 'Reporters report that there is too much news about Obama.',
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


class TestFind(zeit.cms.browser.view.Base):

    def __call__(self):
        zc.resourcelibrary.need('zeit.find')
        return super(TestFind, self).__call__()
