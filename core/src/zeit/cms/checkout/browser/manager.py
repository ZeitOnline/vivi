# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors
import zope.component

import zeit.cms.checkout.interfaces


class Checkout(object):

    def __call__(self):
        checked_out = self.manager.checkout()
        new_url = zope.component.getMultiAdapter((checked_out, self.request),
                                                 name='absolute_url')()
        self.request.response.redirect(new_url + '/@@edit.html')

    @property
    def canCheckout(self):
        return self.manager.canCheckout

    @zope.cachedescriptors.property.Lazy
    def manager(self):
        return zeit.cms.checkout.interfaces.ICheckoutManager(self.context)


class Checkin(object):

    def __call__(self):
        checked_in = self.manager.checkin()
        new_url = zope.component.getMultiAdapter((checked_in, self.request),
                                                 name='absolute_url')()
        self.request.response.redirect(new_url + '/@@view.html')

    @property
    def canCheckin(self):
        return self.manager.canCheckin

    @zope.cachedescriptors.property.Lazy
    def manager(self):
        return zeit.cms.checkout.interfaces.ICheckinManager(self.context)
