# coding: utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component

import zeit.cms.interfaces


class View(object):

    def get_excerpt(self):
        data = self.context.data.strip()
        if len(data) < 100:
            return data
        return data[:100] + u'…'


class Edit(object):

    def __call__(self):
        context_url = zope.component.getMultiAdapter(
            (self.context, self.request),
            name='absolute_url')()
        self.request.response.redirect(
            context_url + '/@@view.html')
        return ''


class Metadata(object):

    @property
    def dav_resource_type(self):
        return zeit.cms.interfaces.IWebDAVReadProperties(self.context).get(
            ('resourcetype', 'DAV:'))


class DragPane(object):

    @property
    def uniqueId(self):
        return self.context.uniqueId

    @property
    def name(self):
        return self.context.__name__
