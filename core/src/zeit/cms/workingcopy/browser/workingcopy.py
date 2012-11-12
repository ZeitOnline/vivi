# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import logging
import zc.table.column
import zc.table.table
import zeit.cms.browser.column
import zeit.cms.browser.listing
import zeit.cms.browser.menu
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.browser.delete
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.traversing
import zope.viewlet.viewlet


log = logging.getLogger(__name__)


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
                log.warning("Could not adapt %r to IListRepresentation",
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

            # This is edge case number something-or-other. Steps to reproduce:
            # - create an object in the repository root folder
            # - check it out
            # - delete the object from the repository
            if unique_id + '/' == zeit.cms.interfaces.ID_NAMESPACE:
                object_in_repository = repository
        else:
            break

    return zope.component.queryMultiAdapter(
        (object_in_repository, schema),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


class ShowOriginal(zeit.cms.browser.menu.ActionMenuItem):

    title = _('Show original')
    sort = -0.9

    def get_url(self):
        url = zope.component.getMultiAdapter(
            (self.content, self.request), name='absolute_url')
        return '%s/@@view.html' % (url, )

    @zope.cachedescriptors.property.Lazy
    def content(self):
        return zeit.cms.interfaces.ICMSContent(self.context.uniqueId, None)

    def render(self):
        if self.content is None:
            return ''
        return super(ShowOriginal, self).render()


class DeleteFromWorkingcopy(zeit.cms.repository.browser.delete.DeleteContent):

    def next_url(self):
        unique_id = self.context.uniqueId
        target = None
        while target is None:
            target = zeit.cms.interfaces.ICMSContent(unique_id, None)
            unique_id = unique_id.rsplit('/', 1)[0]
            if unique_id + '/' == zeit.cms.interfaces.ID_NAMESPACE:
                break
        if target is None:
            target = self.context.__parent__
        return self.url(target)

    def _delete(self):
        zeit.cms.checkout.interfaces.ICheckinManager(self.context).delete()


class DeleteMenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Delete menu item."""

    title = _('Cancel')
