# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

import zope.app.container.interfaces


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
