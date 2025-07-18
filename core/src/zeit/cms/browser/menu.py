import time
import xml.sax.saxutils

import z3c.menu.simple.menu
import zope.app.pagetemplate
import zope.browsermenu.interfaces
import zope.browsermenu.menu
import zope.i18n
import zope.viewlet.interfaces
import zope.viewlet.viewlet

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.view


class OrderedMenu(zope.browsermenu.menu.BrowserMenu):
    def getMenuItems(self, object, request):
        result = []
        for _name, item in zope.component.getAdapters((object, request), self.getMenuItemType()):
            if item.available():
                result.append(item)

        result = sorted(
            result, key=lambda x: (x.order, zope.i18n.translate(x.title, context=request))
        )

        return [
            {
                'title': item.title,
                'description': item.description,
                'action': item.action,
                'selected': 'selected' if item.selected() else '',
                'icon': item.icon,
                'extra': item.extra,
                'submenu': (
                    zope.browsermenu.menu.getMenu(item.submenuId, object, request)
                    if zope.browsermenu.interfaces.IBrowserSubMenuItem.providedBy(item)
                    else None
                ),
            }
            for item in result
        ]


class ExternalActionsMenu(zope.browsermenu.menu.BrowserMenu):
    def getMenuItems(self, object, request):
        result = super().getMenuItems(object, request)
        for item in result:
            item['target'] = '_blank'
            item['rel'] = 'zeit.cms.follow_with_lock'
        return result


class MenuItemBase(zope.viewlet.viewlet.ViewletBase):
    weight = 0

    @property
    def title(self):
        return _(self.__name__)


class ActionMenuItem(MenuItemBase, z3c.menu.simple.menu.SimpleMenuItem):
    """A simple action menu item with icon."""

    template = zope.app.pagetemplate.ViewPageTemplateFile('action-menu-item.pt')
    click_once = True
    item_id = None
    rel = None

    def update(self):
        super().update()
        if self.click_once:
            self.item_id = 'menuitem.%s' % time.time()

    def get_url(self):
        url = zope.component.getMultiAdapter((self.context, self.request), name='absolute_url')
        return '%s/%s' % (url, self.action)

    def img_tag(self):
        img_url = self.icon
        if img_url.startswith('/@@/'):
            # Dereference resource library
            library_name, path = img_url[4:].split('/', 1)
            img_url = zeit.cms.browser.view.resource_url(self.request, library_name, path)
        return '<img src=%s />' % xml.sax.saxutils.quoteattr(img_url)


class MenuViewlet(MenuItemBase):
    menu = None

    @property
    def menu_items(self):
        menu = zope.component.getUtility(zope.browsermenu.interfaces.IBrowserMenu, name=self.menu)
        return menu.getMenuItems(self.context, self.request)


class GlobalMenuItem(MenuItemBase, z3c.menu.simple.menu.GlobalMenuItem):
    """A menu item in the global menu."""

    template = zope.app.pagetemplate.ViewPageTemplateFile('globalmenuitem.pt')

    activeCSS = 'selected'
    inActiveCSS = ''
    pathitem = ''

    @property
    def selected(self):
        app_url = self.request.getApplicationURL()
        url = self.request.getURL()
        path = url[len(app_url) :].split('/')
        if path and self.pathitem in path:
            return True

        return False


class CMSMenuItem(GlobalMenuItem):
    """The CMS menu item which is active when no other item is active."""

    title = _('CMS')
    viewURL = '@@index.html'
    weight = 0

    @property
    def css(self):
        return super().css

    @property
    def selected(self):
        """We are selected when no other item is selected."""
        for viewlet in self.manager.viewlets:
            if viewlet is self:
                continue
            if viewlet.selected:
                return False
        return True


class LightboxActionMenuItem(ActionMenuItem):
    """A menu item rendering a lighbox."""

    template = zope.app.pagetemplate.ViewPageTemplateFile('action-menu-item-with-lightbox.pt')


class DropDownMenuBase:
    weight = 1000
    items_provider = None
    template = zope.app.pagetemplate.ViewPageTemplateFile('secondary_context_actions.pt')
    activeCSS = 'secondary selected'
    inActiveCSS = 'secondary'
    selected = False

    def update(self):
        self.menu_id = 'Menu-%s-%s' % (self.items_provider, time.time())

        provider = zope.component.getMultiAdapter(
            (self.context, self.request, self),
            zope.viewlet.interfaces.IViewletManager,
            self.items_provider,
        )
        provider.update()
        for menu_item in provider.viewlets:
            if menu_item.selected:
                self.selected = True
                break

        self.items = provider.render()


class SecondaryActions(DropDownMenuBase, MenuItemBase):
    """Menu for secondary actions."""

    css = 'secondary-actions'


class GlobalSecondaryActions(DropDownMenuBase, GlobalMenuItem):
    """Menu for global secondary actions."""


class Empty(zope.viewlet.manager.ViewletManagerBase):
    def render(self):
        return ''

    def update(self):
        pass
