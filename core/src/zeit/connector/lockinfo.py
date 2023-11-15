# BBB obsolete, left only until removed from all ZODBs
import persistent
import BTrees.OOBTree

import zope.interface

import zeit.connector.interfaces


@zope.interface.implementer(zeit.connector.interfaces.ILockInfoStorage)
class LockInfo(persistent.Persistent):
    def __init__(self):
        self._storage = BTrees.OOBTree.OOBTree()

    def get(self, id):
        return self._storage.get(id)

    def set(self, id, lockinfo):
        self._storage[id] = lockinfo

    def remove(self, id):
        try:
            del self._storage[id]
        except KeyError:
            pass
