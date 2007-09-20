# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime
import time

import pytz

import persistent.mapping

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
        return LockInfo(object, locked_by, locked_until)

    def setLock(self, object, lock):
        if lock.timeout:
            until = datetime.datetime.fromtimestamp(lock.created + lock.timeout)
        else:
            until = None
        self.connector.lock(object.uniqueId, lock.principal_id, until)

    def delLock(self, object):
        self.connector.unlock(object.uniqueId)

    def cleanup(self):
        pass

    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)


class LockInfo(persistent.mapping.PersistentMapping):

    zope.interface.implements(zeit.cms.content.interfaces.ILockInfo)

    locked_until = None

    def __init__(self, target, principal_id, locked_until=None):
        super(LockInfo, self).__init__()
        self.__parent__ = self.target = target
        self.principal_id = principal_id
        self.created = time.time()
        self.locked_until = locked_until
        if locked_until is not None:
            delta = locked_until - datetime.datetime.now(pytz.UTC)
            self.timeout = (delta.days * 86400
                            + delta.seconds
                            + delta.microseconds * 1e-6)

    def __repr__(self):
        return "<%s.%s object at 0x%x>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            id(self))
