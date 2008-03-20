# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors
import zope.component

import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
from zeit.cms.i18n import MessageFactory as _


class Checkout(zeit.cms.browser.view.Base):

    def __call__(self):
        checked_out = self.manager.checkout()
        self.send_message(_('"${name}" has been checked out.',
                            mapping=dict(name=self.context.__name__)))
        new_url = self.url(checked_out, '@@edit.html')
        self.request.response.redirect(new_url)

    @property
    def canCheckout(self):
        return self.manager.canCheckout

    @zope.cachedescriptors.property.Lazy
    def manager(self):
        return zeit.cms.checkout.interfaces.ICheckoutManager(self.context)


class Checkin(zeit.cms.browser.view.Base):

    def __call__(self):
        checked_in = self.manager.checkin()
        self.send_message(_('"${name}" has been checked in.',
                            mapping=dict(name=checked_in.__name__)))
        new_url = self.url(checked_in, '@@view.html')
        self.request.response.redirect(new_url)

    @property
    def canCheckin(self):
        return self.manager.canCheckin

    @zope.cachedescriptors.property.Lazy
    def manager(self):
        return zeit.cms.checkout.interfaces.ICheckinManager(self.context)
