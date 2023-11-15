import zope.schema
import zope.app.locking.interfaces


class ILockInfo(zope.app.locking.interfaces.ILockInfo):
    """Extended LockInfo interface."""

    locked_until = zope.schema.Datetime(title='Locked Until', required=False)
