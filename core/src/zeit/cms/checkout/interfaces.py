# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component.interfaces
import zope.container.interfaces
import zope.interface


class NotChanged(Exception):
    """Raise in "with checked_out" to indicate that nothing has changed."""


class ICheckoutManager(zope.interface.Interface):
    """Manages workingcopy checkout"""

    canCheckout = zope.interface.Attribute(
        "True if the object can be checked out, False otherwise.")

    def checkout(event=True, temporary=False):
        """Checkout the managed object.

        returns the checked out object.

        - Issues CheckOutEvent if ``event`` is True.

        - If temporary is True the object will be added to a temporary
          workingcopy.

        """


class ICheckinManager(zope.interface.Interface):

    canCheckin = zope.interface.Attribute(
        "True if the object can be checked in, False otherwise.")

    def checkin(event=True, semantic_change=False, ignore_conflicts=False):
        """Checkin the managed object and return the checked in object.

        Checking in effeectively removes the object from the working copy.

        - Issues CheckInEvent if ``event`` is True.

        - If the object's contents was changed in a semantic manner,
          ``semantic_change`` must be True. The ``last_semantic_change``
          property will be updated then.

        - If ``ignore_conflicts`` is True no conflict detection will take
        place.

        """


class IWorkingcopy(zope.container.interfaces.IContainer):
    """The working copy is the area of the CMS where users edit content.

    Objects placed in the workingcopy must provide ILocalContent.
    There is one working copy per user.

    * Adapting IWorkingcopy(principal) should return the workingcopy of the
      given IPrincipal
    * Adapting IWorkingcopy(None) should return the workingcopy of the


    """

class ILocalContent(zope.interface.Interface):
    """Locally (workingcopy) stored content.

    Content which should be stored in a workingcopy needs to be adaptable to
    ILocalContent to create a local copy of the content.

    """


class IRepositoryContent(zope.interface.Interface):
    """Content stored in a repostitory.

    Adapter to place content into the (proper) repository. Adapting content to
    IRepositoryContent returns a new objects *and* places it into the proper
    repository. This is an asymetry to ILocalContent.

    Adding to a repository can raise conflict errors. A named adapter
    'non-conflicting' can be provided.

    Note that objects do not ususally provide this interface, even when they're
    in their repository.

    """


class CheckinCheckoutError(Exception):
    """Raised if there is an error during checkin or checkout.."""

    def __init__(self, uniqueId, *args):
        self.uniqueId = uniqueId
        self.args = args


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
