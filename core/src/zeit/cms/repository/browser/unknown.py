# coding: utf8
import pprint

import zope.component

import zeit.cms.interfaces


class View:
    def get_excerpt(self):
        data = self.context.data.strip()
        if len(data) < 100:
            return data
        return data[:100] + '…'

    def get_properties(self):
        properties = zeit.connector.interfaces.IWebDAVReadProperties(self.context)
        return pprint.pformat(dict(properties))


class Edit:
    def __call__(self):
        context_url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url'
        )()
        self.request.response.redirect(context_url + '/@@view.html')
        return ''


class Metadata:
    @property
    def dav_resource_type(self):
        return zeit.cms.interfaces.IWebDAVReadProperties(self.context).get(
            ('type', 'http://namespaces.zeit.de/CMS/meta')
        )


class DragPane:
    @property
    def uniqueId(self):
        return self.context.uniqueId

    @property
    def name(self):
        return self.context.__name__
