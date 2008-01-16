# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.traversing.browser

import zc.table.column


class LinkColumn(zc.table.column.GetterColumn):

    def __init__(self, title, getter, view='', **kwargs):
        super(LinkColumn, self).__init__(title, getter, **kwargs)
        self.view = view


    def renderCell(self, item, formatter):
        url = zope.traversing.browser.absoluteURL(item, formatter.request)
        title = super(LinkColumn, self).renderCell(item, formatter)
        return '<a href="%s/%s">%s</a>' %(url, self.view, title)
