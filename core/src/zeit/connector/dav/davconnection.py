"""DAV Connection oriented stuff.

To deprecate resource oriented approach, step by step
"""
import davbase
import davresource

class DAVConnection(davbase.DAVConnection):
    "Extends davbase.DavConnection with a couple of methods"
    # XXX Should be integrated into davbase.DavConnection


    # Yeah. We might be tempted to override davbase.DAVConnection's
    # lock() and unlock() methods. After reading up on Pathon's super()
    # I just decided to use new names :-/

    def do_lock(self, url, owner=None, depth=0, timeout=None, headers={}):
        r = davresource.DAVResult(self.lock(url,
                                            owner=owner,
                                            depth=depth,
                                            timeout=timeout,
                                            extra_hdrs=headers))
        if not r.has_errors():
            return r.lock_token
        if r.status == 423:
            raise davresource.DAVLockedError, (r,)
        else:
            raise davresource.DAVLockFailedError, (r,)

    def do_unlock(self, url, locktoken, headers={}):
        if not locktoken:
            raise davresource.DAVInvalidLocktokenError
        r = davresource.DAVResult(self.unlock(url,
                                              locktoken,
                                              extra_hdrs=headers))
        if r.has_errors():
            raise davresource.DAVUnlockFailedError, (r,)
        else:
            return
