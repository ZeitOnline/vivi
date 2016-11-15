from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IRepositoryContent, IFolder
from zeit.cms.workflow.interfaces import IPublishInfo
import zeit.cms.browser.menu
import zope.browsermenu.menu
import zope.i18n


class SortingMenu(zope.browsermenu.menu.BrowserMenu):

    def getMenuItems(self, object, request):
        result = super(SortingMenu, self).getMenuItems(object, request)
        for item in result:
            item['title-translated'] = zope.i18n.translate(
                item['title'], context=request)
        return sorted(result, key=lambda x: x['title-translated'])


class Rename(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Rename menu item."""

    title = _('Rename')


class Delete(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Delete menu item."""

    title = _('Delete')

    @property
    def visible(self):
        if not IRepositoryContent.providedBy(self.context):
            return False
        elif IPublishInfo(self.context).published:
            return False
        elif IFolder.providedBy(self.context):
            for item in self.context.values():
                if IPublishInfo(item).published:
                    return False
        return True

    def render(self):
        if self.visible:
            return super(Delete, self).render()
        else:
            return ''
