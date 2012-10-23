# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import lovely.remotetask.interfaces
import zc.resourcelibrary
import zeit.cms.browser.menu
import zeit.cms.checkout.interfaces
import zeit.cms.workflow.interfaces
import zope.component

class MenuItemBase(object):

    def is_visible(self):
        manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        return manager.canCheckin

    # XXX duplicated from zeit.cms.checkout.browser.MenuItem
    def render(self):
        if self.is_visible():
            zc.resourcelibrary.need('zeit.workflow.publish')
            return super(MenuItemBase, self).render()
        return ''


class MenuItem(MenuItemBase, zeit.cms.browser.menu.LightboxActionMenuItem):

    sort = -1
    lightbox = '@@publish.html'


class Publish(object):

    def can_publish(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return info.can_publish()
