from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IRepositoryContent
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
        return IRepositoryContent.providedBy(self.context) and \
            not IPublishInfo(self.context).published

    def render(self):
        if self.visible:
            return super(Delete, self).render()
        else:
            return ''
