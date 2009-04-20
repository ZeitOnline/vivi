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
                  'teaser_title': 'Obama still alive',
                  'teaser_text': 'Obama is still alive and well.'},
                 {'uniqueId': 'bar',
                  'teaser_title': 'Obama journalism too extreme',
                  'teaser_text': 'Reporters report that there is too much news about Obama.'}]
                 }
        return cjson.encode(result)


class TestFind(zeit.cms.browser.view.Base):

    def __call__(self):
        zc.resourcelibrary.need('zeit.find')
        return super(TestFind, self).__call__()
