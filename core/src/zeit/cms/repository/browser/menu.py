# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
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
