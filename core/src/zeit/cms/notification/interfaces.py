# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface


class IPrincipalNotifications(zope.interface.Interface):

    def add(notification):
        """Add notification."""

    def __iter__():
        """Iterate over notifiactions.

        Sorted by notification time.

        """
