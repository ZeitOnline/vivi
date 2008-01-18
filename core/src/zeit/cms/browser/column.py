# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import cgi

import zope.interface
import zope.traversing.browser
from zope.app import zapi

import zc.table.column
import zc.table.interfaces


class LinkColumn(zc.table.column.GetterColumn):
    """A column which displays a link to a value.
    """

    zope.interface.implements(zc.table.interfaces.ISortableColumn)

    def __init__(self, view='', css_class=None, **kw):
        super(LinkColumn, self).__init__(**kw)
        self.view = view
        if css_class:
            self.css_class = css_class

    def renderCell(self, item, formatter):
        # Get the target object and compute the URL
        target = self.getter(item, formatter)
        if target is None:
            return u''

        # Get the same display as if a normal column.
        content = cgi.escape(
            unicode(super(LinkColumn, self).renderCell(item, formatter)))

        # Try to get a URL, if we can't then ignore setting up a link.
        try:
            url = zapi.absoluteURL(target, formatter.request)
        except TypeError:
            result = content
        else:
            if self.view:
                url = '%s/%s' % (url, self.view)
            css_class = self.css_class(target, item, formatter) or ''
            if css_class:
                css_class = 'class="%s" ' % css_class
            result = u'<a %shref="%s">%s</a>' % (css_class, url, content)
        return result

    def cell_formatter(self, value, item, formatter):
        return value.title

    def getSortKey(self, item, formatter):
        return self.cell_formatter(
            self.getter(item, formatter), item, formatter)

    def css_class(self, value, item, formatter):
        return u''
