# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface


class IPurge(zope.interface.Interface):
    """Adapter to purge objects from a cache."""

    def purge():
        """Purge."""
