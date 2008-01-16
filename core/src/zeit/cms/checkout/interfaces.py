# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component.interfaces
import zope.interface


class ICheckoutManager(zope.interface.Interface):
    """Manages workingcopy checkout"""

    canCheckout = zope.interface.Attribute(
        "True if the object can be checked out, False otherwise.")

    def checkout(event=True):
        """Checkout the managed object.


        returns the checked out object.

        Issues CheckOutEvent if `event` is True.
        """


class ICheckinManager(zope.interface.Interface):

    canCheckin = zope.interface.Attribute(
        "True if the object can be checked in, False otherwise.")

    def checkin(event=True):
        """Checkin the managed object and return the checked in object.

        Checking in effeectively removes the object from the working copy.

        Issues CheckInEvent if `event` is True.

        """


class CheckinCheckoutError(Exception):
    """Raised if there is an error during checkin or checkout.."""


class ICheckinCheckoutEvent(zope.component.interfaces.IObjectEvent):
    """Generated when a content object is checked in or out."""

    principal = zope.interface.Attribute(
        "The principal checking out the content object")


class ICheckoutEvent(ICheckinCheckoutEvent):
    """Generated when a content object was checked out."""


class ICheckinEvent(ICheckinCheckoutEvent):
    """Generated when a content object was checked in."""


class EventBase(zope.component.interfaces.ObjectEvent):

    def __init__(self, object, principal):
        super(EventBase, self).__init__(object)
        self.principal = principal


class CheckoutEvent(EventBase):
    """Generated when a content object is checked out."""

    zope.interface.implements(ICheckoutEvent)


class CheckinEvent(EventBase):
    """Generated when a content object is checked in."""

    zope.interface.implements(ICheckinEvent)
