# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent
import BTrees.OOBTree

import zope.interface

import zeit.connector.interfaces


class LockInfo(persistent.Persistent):

    zope.interface.implements(zeit.connector.interfaces.ILockInfoStorage)

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
