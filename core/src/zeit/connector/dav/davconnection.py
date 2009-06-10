import zeit.connector.dav.davbase
import zeit.connector.dav.davresource
import zeit.connector.dav.interfaces

class DAVConnection(zeit.connector.dav.davbase.DAVConnection):
    """DAV Connection oriented.

    (as opposed to resource oriented)
    """

    # Yeah. We might be tempted to override davbase.DAVConnection's
    # lock() and unlock() methods. After reading up on Pathon's super()
    # I just decided to use new names :-/

    def lock(self, url, owner=None, depth=0, timeout=None, headers={}):
        r = self.get_result(
            'lock', url, owner=owner, depth=depth, timeout=timeout,
            extra_hdrs=headers)
        if not r.has_errors():
            return r.lock_token
        if r.status == 423:
            raise zeit.connector.dav.interfaces.DAVLockedError(r)
        raise zeit.connector.dav.interfaces.DAVLockFailedError(r)

    def unlock(self, url, locktoken, headers={}):
        if not locktoken:
            raise zeit.connector.dav.interfaces.DAVInvalidLocktokenError()
        r = self.get_result('unlock', url, locktoken, extra_hdrs=headers)
        if r.has_errors():
            raise zeit.connector.dav.interfaces.DAVUnlockFailedError(r)

    def propfind(self, *args, **kwargs):
        return self.get_rsult('propfind', *args, **kwargs)

    def get_result(self, method_name, *args, **kwargs):
        method = getattr(super(DAVConnection, self), method_name)
        response = method(*args, **kwargs)
        return zeit.connector.dav.davresource.DAVResult(response)
