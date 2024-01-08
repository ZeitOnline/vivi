import logging

import grokcore.component as grok
import zope.cachedescriptors.property
import zope.component
import zope.viewlet.viewlet

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.interfaces
import zeit.cms.browser.menu
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.browser.delete
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces


log = logging.getLogger(__name__)


class Sidebar(zope.viewlet.viewlet.ViewletBase):
    """view class for navtree"""

    @property
    def workingcopy(self):
        return zeit.cms.workingcopy.interfaces.IWorkingcopy(self.request.principal)

    @zope.cachedescriptors.property.Lazy
    def content(self):
        result = []
        for obj in self.workingcopy.values():
            list_repr = zope.component.queryMultiAdapter(
                (obj, self.request), zeit.cms.browser.interfaces.IListRepresentation
            )
            if list_repr is None:
                log.warning('Could not adapt %r to IListRepresentation', (obj,))
                continue
            css_class = []
            if list_repr.type:
                css_class.append('type-' + list_repr.type)
            if zeit.cms.clipboard.interfaces.IObjectReference.providedBy(obj):
                css_class.append('reference')
            result.append(
                {
                    'css_class': ' '.join(css_class),
                    'obj': obj,
                    'title': list_repr.title or list_repr.__name__,
                    'uniqueId': list_repr.uniqueId,
                    'url': list_repr.url,
                }
            )
        return result


@zope.component.adapter(
    zeit.cms.workingcopy.interfaces.ILocalContent, zeit.cms.content.interfaces.ICMSContentSource
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def localcontent_default_browsing_location(context, schema):
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

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
        (object_in_repository, schema), zeit.cms.browser.interfaces.IDefaultBrowsingLocation
    )


@grok.adapter(zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
@grok.implementer(zeit.cms.browser.interfaces.IAdditionalLayer)
def layer_for_workingcopy(context):
    return zeit.cms.browser.interfaces.IWorkingcopyLayer


class DeleteFromWorkingcopy(zeit.cms.repository.browser.delete.DeleteContent):
    def next_url(self, folder):
        unique_id = self.context.uniqueId
        target = None
        while target is None:
            target = zeit.cms.interfaces.ICMSContent(unique_id, None)
            unique_id = unique_id.rsplit('/', 1)[0]
            if unique_id + '/' == zeit.cms.interfaces.ID_NAMESPACE:
                break
        if target is None:
            target = folder
        return self.url(target)

    def _delete(self):
        zeit.cms.checkout.interfaces.ICheckinManager(self.context).delete()


class DeleteMenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Delete menu item."""

    title = _('Cancel workingcopy')
