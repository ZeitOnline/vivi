# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""View baseclass. Greatly inspired and copied from grok.

"""

import zope.component

import z3c.flashmessage.interfaces


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

    def redirect(self, url):
        return self.request.response.redirect(url)

    def send_message(self, message, type='message'):
        source = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource, name='session')
        source.send(message, type)
