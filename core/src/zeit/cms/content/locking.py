# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.app.locking.interfaces

import zeit.connector.interfaces

class LockStorage(object):

    zope.interface.implements(zope.app.locking.interfaces.ILockStorage)

    def getLock(self, object):
        try:
            locked_by, locked_until, my_lock = self.connector.locked(
                object.uniqueId)
        except KeyError:
            # resource does not exist -> no lock
            return None
        if locked_by is None:
            return None
        delta = locked_until - datetime.datetime.now()
        timeout = (delta.days * 86400
                   + delta.seconds
                   + delta.microseconds * 1e-6)
        return zope.app.locking.lockinfo.LockInfo(None, locked_by, timeout)

    def setLock(self, object, lock):
        until = datetime.datetime.fromtimestamp(lock.created + lock.timeout)
        self.connector.lock(object.uniqueId, lock.principal_id, until)

    def delLock(self, object):
        self.connector.unlock(object.uniqueId)

    def cleanup(self):
        pass

    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)
