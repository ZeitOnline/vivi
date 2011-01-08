# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface


class PurgeError(Exception):
    """Raised when there was an error while purging."""

    def __init__(self, server, message):
        self.server = server
        self.message = message

    def __str__(self):
        return "[%s] %s" % (self.server, self.message)


class IPurge(zope.interface.Interface):
    """Adapter to purge objects from a cache."""

    def purge():
        """Purge."""
