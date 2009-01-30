# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Menu infrastructure."""

import time
import xml.sax.saxutils

import zope.viewlet.interfaces
import zope.viewlet.viewlet

import zope.app.pagetemplate
import zope.app.publisher.browser.menu
import zope.app.publisher.interfaces.browser

import z3c.menu.simple.menu

from zeit.cms.i18n import MessageFactory as _


class ExternalActionsMenu(zope.app.publisher.browser.menu.BrowserMenu):

    def getMenuItems(self, object, request):
        result = super(ExternalActionsMenu, self).getMenuItems(object, request)
        for item in result:
            item['target'] = "_blank"
        return result


class MenuItemBase(zope.viewlet.viewlet.ViewletBase):

    sort = 0
    def __cmp__(self, other):
        __traceback_info__ = (self, other)
        return cmp(float(self.sort), float(other.sort))


class ActionMenuItem(MenuItemBase, z3c.menu.simple.menu.SimpleMenuItem):
    """A simple action menu item with icon."""

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'action-menu-item.pt')

    def get_url(self):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')
        return '%s/%s' % (url, self.action)


class MenuViewlet(MenuItemBase):

    menu = None

    @property
    def menu_items(self):
        menu = zope.component.getUtility(
            zope.app.publisher.interfaces.browser.IBrowserMenu,
            name=self.menu)
        return menu.getMenuItems(self.context, self.request)


class GlobalMenuItem(MenuItemBase, z3c.menu.simple.menu.GlobalMenuItem):
    """A menu item in the global menu."""

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'globalmenuitem.pt')

    activeCSS = 'selected'
    inActiveCSS = ''
    pathitem = ''

    @property
    def selected(self):
        app_url = self.request.getApplicationURL()
        url = self.request.getURL()
        path = url[len(app_url):].split('/')
        if path and self.pathitem in path:
            return True

        return False


class CMSMenuItem(GlobalMenuItem):
    """The CMS menu item which is active when no other item is active."""

    title = _("CMS")
    viewURL = "@@index.html"
    sort = 0

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

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'action-menu-item-with-lightbox.pt')

    def img_tag(self):
        return '<img src=%s />' % xml.sax.saxutils.quoteattr(self.icon)


class DropDownMenuBase(object):

    sort = 1000
    items_provider = None
    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'secondary_context_actions.pt')
    activeCSS = 'secondary selected'
    inActiveCSS = 'secondary'
    selected = False

    def update(self):
        self.menu_id = 'Menu-%s-%s' % (self.items_provider, time.time())

        provider = zope.component.getMultiAdapter(
            (self.context, self.request, self),
            zope.viewlet.interfaces.IViewletManager,
            self.items_provider)
        provider.update()
        for menu_item in provider.viewlets:
            if menu_item.selected:
                self.selected = True
                break

        self.items = provider.render()



class SecondaryActions(DropDownMenuBase, MenuItemBase):
    """Menu for secondary actions."""

    css = None

class GlobalSecondaryActions(DropDownMenuBase, GlobalMenuItem):
    """Menu for global secondary actions."""
