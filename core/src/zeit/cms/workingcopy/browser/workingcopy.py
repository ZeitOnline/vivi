# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.viewlet.viewlet
import zope.traversing

import zc.table.table
import zc.table.column

import zeit.cms.browser.column
import zeit.cms.browser.listing
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces


class Sidebar(zope.viewlet.viewlet.ViewletBase,
              zeit.cms.browser.listing.Listing):
    """view class for navtree"""
    columns = (
        zeit.cms.browser.listing.TypeColumn(u''),
        zeit.cms.browser.column.LinkColumn(
            u'Titel',
            lambda t, c: t.title,
            view='edit.html'),
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
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def localcontent_default_browsing_location(context, schema):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)

    # Get the object in the repository, potentially looking for the parent.
    object_in_repository = None
    unique_id = context.uniqueId
    while object_in_repository is None:
        try:
            object_in_repository = repository.getContent(unique_id)
        except KeyError:
            unique_id = unique_id.rsplit('/', 1)[0]
        else:
            break

    return zope.component.queryMultiAdapter(
        (object_in_repository, schema),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
