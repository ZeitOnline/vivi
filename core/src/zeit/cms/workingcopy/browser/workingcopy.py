# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging

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
from zeit.cms.i18n import MessageFactory as _


logger = logging.getLogger(__name__)


class Sidebar(zope.viewlet.viewlet.ViewletBase,
              zeit.cms.browser.listing.Listing):
    """view class for navtree"""

    css_class = 'hasMetadata'

    columns = (
        zeit.cms.browser.listing.TypeColumn(u''),
        zeit.cms.browser.column.LinkColumn(
            title=_('Title'),
            getter=lambda i, f: i.context,
            cell_formatter=lambda v, i, f: i.title or i.__name__,
            css_class=lambda v, i, f: i.type,
            view='edit.html'),
        zeit.cms.browser.listing.MetadataColumn(searchable_text=False),
        )

    def render(self):
        return self.index()

    @property
    def table(self):
        formatter = zc.table.table.Formatter(
            self.context, self.request, self.content, columns=self.columns)
        formatter.cssClasses['table'] = self.css_class
        return formatter

    @property
    def workingcopy(self):
        return zeit.cms.workingcopy.interfaces.IWorkingcopy(
            self.request.principal)

    @property
    def content(self):
        result = []
        for obj in self.workingcopy.values():
            list_repr = zope.component.queryMultiAdapter(
                (obj, self.request),
                zeit.cms.browser.interfaces.IListRepresentation)
            if list_repr is None:
                logger.warning("Could not adapt %r to IListRepresentation",
                               (obj, ))
            else:
                result.append(list_repr)
        return result


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
