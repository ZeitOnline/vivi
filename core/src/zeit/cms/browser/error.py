# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.resources
import zope.i18n


class ErrorView(object):

    def __call__(self):
        self.request.response.setStatus(500)
        zeit.cms.browser.resources.error_css.need()
        return self.index()

    def message(self):
        args = getattr(self.context, 'args', None)
        if args:
            message = zope.i18n.translate(
                args[0], context=self.request)
        else:
            message = self.context

        return '%s: %s' % (self.context.__class__.__name__, message)
