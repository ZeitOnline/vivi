# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zope.cachedescriptors
import zope.component
from zeit.cms.i18n import MessageFactory as _


class Checkout(zeit.cms.browser.view.Base):

    def __call__(self):
        checked_out = self.manager.checkout()
        self.send_message(_('"${name}" has been checked out.',
                            mapping=dict(name=self.context.__name__)))

        new_view = None
        came_from = self.request.form.get('came_from')
        if came_from is not None:
            new_view = zope.component.queryAdapter(
                self.context,
                zeit.cms.browser.interfaces.IEditViewName,
                name=came_from)
        if new_view is None:
            new_view = 'edit.html'
        new_url = self.url(checked_out, '@@' + new_view)
        self.request.response.redirect(new_url)

    @property
    def canCheckout(self):
        return self.manager.canCheckout

    @zope.cachedescriptors.property.Lazy
    def manager(self):
        return zeit.cms.checkout.interfaces.ICheckoutManager(self.context)


class Checkin(zeit.cms.browser.view.Base):

    def __call__(self):
        checked_in = self.manager.checkin(semantic_change=True)
        self.send_message(_('"${name}" has been checked in.',
                            mapping=dict(name=checked_in.__name__)))
        new_view = None
        came_from = self.request.form.get('came_from')
        if came_from is not None:
            new_view = zope.component.queryAdapter(
                self.context,
                zeit.cms.browser.interfaces.IDisplayViewName,
                name=came_from)
        if new_view is None:
            new_view = 'view.html'
        new_url = self.url(checked_in, '@@' + new_view)
        self.request.response.redirect(new_url)

    @property
    def canCheckin(self):
        return self.manager.canCheckin

    @zope.cachedescriptors.property.Lazy
    def manager(self):
        return zeit.cms.checkout.interfaces.ICheckinManager(self.context)


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):

    sort = -1

    @property
    def action(self):
        view_name = self.__parent__.__name__
        return '@@%s?came_from=%s' % (self.base_action, view_name)

    def render(self):
        if self.is_visible():
            return super(MenuItem, self).render()
        return ''


class CheckoutMenuItem(MenuItem):
    """MenuItem for checking out."""

    title = _('Checkout ^O')
    base_action = 'checkout'
    accesskey = 'o'

    def is_visible(self):
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(self.context)
        return manager.canCheckout


class CheckinMenuItem(MenuItem):
    """MenuItem for checking in."""

    title = _('Checkin ^I')
    base_action = 'checkin'
    accesskey = 'i'

    def is_visible(self):
        manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        return manager.canCheckin
