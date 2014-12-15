# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.resources
import zope.i18n


class ErrorView(object):

    status = 500

    def __call__(self):
        self.request.response.setStatus(self.status)
        if self.is_xhr:
            # XXX Using a json response would be cleaner.
            self.request.response.setHeader('Content-Type', 'text/plain')
            return self.message
        else:
            zeit.cms.browser.resources.error_css.need()
            return super(ErrorView, self).__call__()

    @property
    def is_xhr(self):
        # Copied from webob.request.Request.is_xhr
        return self.request.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    @property
    def message(self):
        args = getattr(self.context, 'args', None)
        if args:
            message = zope.i18n.translate(
                args[0], context=self.request)
        else:
            message = self.context

        return '%s: %s' % (self.context.__class__.__name__, message)
