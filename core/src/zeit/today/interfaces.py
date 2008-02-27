# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface


class ICountStorage(zope.interface.Interface):
    """Central access to click counting.

    This utility takes care of refreshing and caching today.xml.

    """

    def get_count(unique_id):
        """Return access count for given unique id.

        returns amount of hits (int) or None if nothing is known about the
        given unique_id.

        """
