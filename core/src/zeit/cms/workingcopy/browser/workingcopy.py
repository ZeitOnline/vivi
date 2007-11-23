# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.viewlet.viewlet
import zope.traversing

import zc.table.table
import zc.table.column

import zeit.cms.browser.listing
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces

class LinkColumn(zc.table.column.GetterColumn):

  def renderCell(self, item, formatter):
      url = zope.traversing.browser.absoluteURL(item, item.request)
      title = super(LinkColumn, self).renderCell(item, formatter)
      return '<a href="%s/@@edit.html">%s</a>' %(url, title)


class Sidebar(zope.viewlet.viewlet.ViewletBase,
              zeit.cms.browser.listing.Listing):
    """view class for navtree"""
    columns = (
        zeit.cms.browser.listing.TypeColumn(u''),
        LinkColumn(
            u'Titel',
            lambda t, c: t.title),
        )

    def render(self):
        return self.index()

    @property
    def table(self):
        return zc.table.table.Formatter(
            self.context, self.request, self.content, columns=self.columns)

    @property
    def workingcopy(self):
        return zeit.cms.workingcopy.interfaces.IWorkingcopy(
            self.request.principal)

    contentContext = workingcopy


@zope.component.adapter(
    zeit.cms.workingcopy.interfaces.ILocalContent,
    zeit.cms.interfaces.ICMSContentType)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def localcontent_default_browsing_location(context, schema):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    object_in_repository = repository.getContent(context.uniqueId)
    return zope.component.queryMultiAdapter(
        (object_in_repository, schema),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
