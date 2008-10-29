# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$


class ErrorView(object):

    def __call__(self):
        self.request.response.setStatus(500)
        return self.index()

    def message(self):
        return '%s: %s' % (self.context.__class__.__name__, self.context)
