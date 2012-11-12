# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
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

    last_validation_error = zope.interface.Attribute(
        """If canCheckin returned False, this may contain an error message,
        it's None otherwise.
        Note that you need to "call" canCheckin before this is filled in.
        """)

    def checkin(event=True, semantic_change=None, ignore_conflicts=False):
        """Check in the managed object and return the checked-in object.

        Checking in effectively removes the object from the working copy.

        - Issues CheckInEvent if ``event`` is True.

        - If the context object's contents was changed in a semantic manner,
          this may be signalled by the ``semantic_change`` parameter. The
          ``last_semantic_change`` property will be updated in that case.
          Alternatively, if ``semantic_change`` is None,
          ``ISemanticChange(context).has_semantic_change`` is inspected.

        - If ``ignore_conflicts`` is True, no conflict detection will take
          place.

        """

    def delete():
        """Delete the managed object from the working copy.

        Announces working-copy deletion issuing IBeforeDeleteEvent and
        IAfterDeleteEvent.

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

    publishing = zope.interface.Attribute(
        """"True if this checkin happens during publishing.

        Event handlers can use this to prevent infinite loops (since another
        checkout/checkin cycle happens during publishing to update XML
        references etc.).""")


class IBeforeCheckoutEvent(ICheckinCheckoutEvent):
    """Generated just before a content object is checked out."""


class IAfterCheckoutEvent(ICheckinCheckoutEvent):
    """Generated when a content object was checked out."""

    publishing = zope.interface.Attribute(
        """NOTE: this common checkin/checkout attribute does not apply for
        this event""")


class IValidateCheckinEvent(ICheckinCheckoutEvent):
    """Allows subscribers to influence whether a content object can be checked
    in."""

    def veto(message=None):
        """Signals that a checkin is not allowed."""

    publishing = zope.interface.Attribute(
        """NOTE: this common checkin/checkout attribute does not apply for
        this event""")


class IBeforeCheckinEvent(ICheckinCheckoutEvent):
    """Generated just before a content object is checked in."""


class IAfterCheckinEvent(ICheckinCheckoutEvent):
    """Generated when a content object was checked in."""


class IBeforeDeleteEvent(ICheckinCheckoutEvent):
    """Generated just before a content object is deleted."""


class IAfterDeleteEvent(ICheckinCheckoutEvent):
    """Generated when a content object was deleted."""


class EventBase(zope.component.interfaces.ObjectEvent):

    def __init__(self, object, workingcopy, principal, publishing=False):
        super(EventBase, self).__init__(object)
        self.workingcopy = workingcopy
        self.principal = principal
        self.publishing = publishing


class BeforeCheckoutEvent(EventBase):

    zope.interface.implements(IBeforeCheckoutEvent)


class AfterCheckoutEvent(EventBase):

    zope.interface.implements(IAfterCheckoutEvent)


class ValidateCheckinEvent(EventBase):

    zope.interface.implements(IValidateCheckinEvent)

    def __init__(self, *args, **kw):
        super(ValidateCheckinEvent, self).__init__(*args, **kw)
        self.vetoed = None

    def veto(self, message=None):
        if message == None:
            message = _('not allowed')
        self.vetoed = message


class BeforeCheckinEvent(EventBase):

    zope.interface.implements(IBeforeCheckinEvent)


class AfterCheckinEvent(EventBase):

    zope.interface.implements(IAfterCheckinEvent)


class BeforeDeleteEvent(EventBase):

    zope.interface.implements(IBeforeDeleteEvent)


class AfterDeleteEvent(EventBase):

    zope.interface.implements(IAfterDeleteEvent)
