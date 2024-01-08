import zope.browsermenu.menu
import zope.i18n

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.browser.delete import folder_can_be_deleted
from zeit.cms.repository.interfaces import IFolder, IRepositoryContent
from zeit.cms.workflow.interfaces import IPublishInfo
import zeit.cms.browser.menu


class SortingMenu(zope.browsermenu.menu.BrowserMenu):
    def getMenuItems(self, object, request):
        result = super().getMenuItems(object, request)
        for item in result:
            item['title-translated'] = zope.i18n.translate(item['title'], context=request)
        return sorted(result, key=lambda x: x['title-translated'])


class Delete(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Delete menu item."""

    title = _('Delete')

    @property
    def visible(self):
        if not IRepositoryContent.providedBy(self.context) or IPublishInfo(self.context).published:
            return False
        if IFolder.providedBy(self.context):
            return folder_can_be_deleted(self.context)
        return True

    def render(self):
        if self.visible:
            return super().render()
        else:
            return ''
