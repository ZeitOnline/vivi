# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component.interfaces
import zope.interface


class ICheckoutManager(zope.interface.Interface):
    """Manages workingcopy checkout"""

    canCheckout = zope.interface.Attribute(
        "True if the object can be checked out, False otherwise.")

    def checkout(event=True, temporary=False):
        """Checkout the managed object.

        returns the checked out object.

        Issues CheckOutEvent if `event` is True.
        If temporary is True the object will be added to a temporary
        workingcopy.

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


class IBeforeCheckoutEvent(ICheckinCheckoutEvent):
    """Generated when a content object was checked out."""


class IAfterCheckoutEvent(ICheckinCheckoutEvent):
    """Generated when a content object was checked out."""


class IBeforeCheckinEvent(ICheckinCheckoutEvent):
    """Generated when a content object was checked in."""


class IAfterCheckinEvent(ICheckinCheckoutEvent):
    """Generated when a content object was checked in."""

    old_object = zope.interface.Attribute("The obect before checkin.")


class EventBase(zope.component.interfaces.ObjectEvent):

    def __init__(self, object, workingcopy, principal):
        super(EventBase, self).__init__(object)
        self.workingcopy = workingcopy
        self.principal = principal


class BeforeCheckoutEvent(EventBase):
    """Generated before a content object is checked out."""

    zope.interface.implements(IBeforeCheckoutEvent)


class AfterCheckoutEvent(EventBase):
    """Generated after a content object was checked out."""

    zope.interface.implements(IAfterCheckoutEvent)


class BeforeCheckinEvent(EventBase):
    """Generated before a content object is checked in."""

    zope.interface.implements(IBeforeCheckinEvent)


class AfterCheckinEvent(EventBase):
    """Generated after a content object was checked in."""

    zope.interface.implements(IAfterCheckinEvent)
