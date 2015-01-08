import datetime
import grokcore.component
import persistent.mapping
import pytz
import time
import zeit.cms.interfaces
import zeit.cms.locking.interfaces
import zeit.cms.repository.interfaces
import zeit.connector.interfaces
import zope.app.locking.adapter
import zope.app.locking.interfaces
import zope.component
import zope.interface


class LockStorage(object):

    zope.interface.implements(zope.app.locking.interfaces.ILockStorage)

    def getLock(self, object):
        if not zeit.cms.interfaces.ICMSContent.providedBy(object):
            # Non cms objects cannot have locks.
            return None
        try:
            locked_by, locked_until, my_lock = self.connector.locked(
                object.uniqueId)
        except (KeyError, ValueError):
            # resource does not exist -> no lock
            return None
        if locked_by is None and locked_until is None:
            return None
        if locked_by is None:
            locked_by = u'zeit.cms.unknown-dav-locker'
        if not my_lock:
            locked_by = "othersystem." + locked_by

        return LockInfo(object, locked_by, locked_until)

    def setLock(self, object, lock):
        if not zeit.cms.interfaces.ICMSContent.providedBy(object):
            # Non cms objects cannot have locks.
            raise ValueError("Non CMS objects cannot be locked.")
        if lock.timeout:
            until = datetime.datetime.fromtimestamp(
                lock.created + lock.timeout, pytz.UTC)
        else:
            until = None
        try:
            self.connector.lock(object.uniqueId, lock.principal_id, until)
        except zeit.connector.interfaces.LockingError, e:
            raise zope.app.locking.interfaces.LockingError(e.uniqueId, *e.args)
        # Now make sure the object *really* exists. In case we've create a null
        # resource lock, we unlock and raise an error
        if not self.connector[object.uniqueId].properties.get(
            ('getlastmodified', 'DAV:')):
            self.delLock(object)
            raise zope.app.locking.interfaces.LockingError(
                object.uniqueId, 'Object does not exist.')

    def delLock(self, object):
        if not zeit.cms.interfaces.ICMSContent.providedBy(object):
            # Non cms objects cannot have locks.
            return
        self.connector.unlock(object.uniqueId)

    def cleanup(self):
        pass

    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)


class LockInfo(persistent.mapping.PersistentMapping):

    zope.interface.implements(zeit.cms.locking.interfaces.ILockInfo)

    locked_until = None

    def __init__(self, target, principal_id, locked_until=None):
        super(LockInfo, self).__init__()
        self.__parent__ = self.target = target
        self.principal_id = principal_id
        self.created = time.time()
        self.locked_until = locked_until
        if isinstance(locked_until, datetime.datetime):
            delta = locked_until - datetime.datetime.now(pytz.UTC)
            self.timeout = (delta.days * 86400
                            + delta.seconds
                            + delta.microseconds * 1e-6)

    def __repr__(self):
        return "<%s.%s object at 0x%x>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            id(self))


class CMSLockingAdapter(zope.app.locking.adapter.LockingAdapter):
    """Special locking adapter with different security."""

    zope.component.adapts(zeit.cms.repository.interfaces.IRepositoryContent)
    zope.interface.implements(zope.app.locking.interfaces.ILockable)

    __repr__ = object.__repr__


@grokcore.component.adapter(zeit.cms.interfaces.ICMSContent)
@grokcore.component.implementer(zope.app.locking.interfaces.ILockable)
def no_general_locking(context):
    return None
