# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.container.interfaces
import zope.interface


class IWorkingcopy(zope.app.container.interfaces.IContainer):
    """The working copy is the area of the CMS where users edit content.

    There is one working copy per user.

    """


class IWorkingcopyLocation(zope.app.container.interfaces.IContainer):
    """Location for working copies of all users."""


    def getWorkingcopy():
        """Get the working copy for the currently logged in principal."""

    def getWorkingcopyFor(principal):
        """Get the working copy for `principal`."""


class ILocalContent(zope.interface.Interface):
    """Marker interface for locally stored content."""
