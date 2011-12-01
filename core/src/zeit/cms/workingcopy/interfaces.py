# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.container.interfaces
import zope.interface

# BBB:
from zeit.cms.checkout.interfaces import IWorkingcopy, ILocalContent


class IWorkingcopyLocation(zope.app.container.interfaces.IContainer):
    """Location for working copies of all users."""

    def getWorkingcopy():
        """Get the working copy for the currently logged in principal."""

    def getWorkingcopyFor(principal):
        """Get the working copy for `principal`."""
