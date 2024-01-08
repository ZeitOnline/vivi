import zope.container.interfaces
import zope.interface

# BBB:
from zeit.cms.checkout.interfaces import ILocalContent, IWorkingcopy  # noqa


class IWorkingcopyLocation(zope.container.interfaces.IContainer):
    """Location for working copies of all users."""

    def getWorkingcopy():
        """Get the working copy for the currently logged in principal."""

    def getWorkingcopyFor(principal):
        """Get the working copy for `principal`."""
