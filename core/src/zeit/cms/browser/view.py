# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""View baseclass. Greatly inspired and copied from grok.

"""

import cjson
import z3c.flashmessage.interfaces
import zope.component


class Base(object):

    def url(self, obj=None, name=None):
        # if the first argument is a string, that's the name. There should
        # be no second argument
        if isinstance(obj, basestring):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if name is None and obj is None:
            # create URL to view itself
            obj = self
        elif name is not None and obj is None:
            # create URL to view on context
            obj = self.context
        url = zope.component.getMultiAdapter(
            (obj, self.request), name='absolute_url')()
        if name is None:
            return url
        return '%s/%s' % (url, name)

    def redirect(self, url, status=None, trusted=False):
        assert status is None or isinstance(status, int)
        return self.request.response.redirect(
            url, status=status, trusted=trusted)

    def send_message(self, message, type='message'):
        source = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource, name='session')
        source.send(message, type)


class JSON(Base):

    resource_library = None
    template = None

    def __call__(self):
        # XXX application/json would be correct
        self.request.response.setHeader('Content-Type', 'text/json')
        result = self.json()

        # use template indicated in JSON if it's there,
        # otherwise use class template
        if isinstance(result, dict):
            template = result.pop('template', None)
            if template is None:
                template = self.template
            if template is not None:
                result['template_url'] = self.resources[template]()
        return cjson.encode(result)

    def json(self):
        return {}

    @property
    def resources(self):
        return zope.component.getAdapter(
            self.request, zope.interface.Interface,
            name=self.resource_library)
