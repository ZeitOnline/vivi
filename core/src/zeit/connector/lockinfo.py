# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persisent
import BTrees.OOBTree



class ILockTokenStorage(zope.interface.Interface):
    """Storage for locktokens."""

    def get(id):
        """Return lockinfo for given id.

        returns (token, principal, time)

        """

    def set(id, lockinfo):
        """Add lockinfo to storage.

        lockinfo: triple of (token, principal, time)

        """

    def del(id):
        """Remove lockinfo for id.

        It is not an error to remove no existing lockinfos."""



class LockInfo(persistent.Persisent):

    def __init__(self):
        self._storage = BTrees.OOBTree.OOBTree()

    def get(id)


