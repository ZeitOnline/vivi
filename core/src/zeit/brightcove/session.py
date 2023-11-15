import threading
import time
import transaction
import transaction.interfaces
import zeit.brightcove.interfaces
import zope.component
import zope.interface


def get():
    if not hasattr(_holder, 'session'):
        _holder.session = Session()
    return _holder.session


_holder = threading.local()


@zope.interface.implementer(zeit.brightcove.interfaces.ISession)
class Session:
    def __init__(self):
        self.items = []
        self._needs_to_join = True

    # DataManager protocol methods

    def reset(self):
        self.items[:] = []
        self._needs_to_join = True

    def join_transaction(self):
        if not self._needs_to_join:
            return
        dm = APIDataManager(self)
        transaction.get().join(dm)
        self._needs_to_join = False

    def flush(self):
        api = zope.component.getUtility(zeit.brightcove.interfaces.ICMSAPI)
        try:
            for method, args, kw in self.items:
                getattr(api, method)(*args, **kw)
        finally:
            self.reset()

    # Client methods

    def update_video(self, *args, **kw):
        self.join_transaction()
        self.items.append(('update_video', args, kw))


@zope.interface.implementer(transaction.interfaces.ISavepointDataManager)
class APIDataManager:
    """Data manager for a transaction-less store, we try to run as the last 2PC
    participant and persist our changes in commit() (because we have no other
    choice), thus when we have an error, the other participants then can roll
    back.
    """

    def __init__(self, session):
        self.session = session

    def abort(self, transaction):
        self.session.reset()

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        self.session.flush()

    def tpc_abort(self, transaction):
        self.session.reset()

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        pass

    def sortKey(self):
        # Try to sort last, so that we vote last.
        return '~zeit.brightcove:%f' % time.time()

    def savepoint(self):
        return NoOpSavepoint()

    def __repr__(self):
        return '<%s.%s for %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            transaction.get(),
        )


@zope.interface.implementer(transaction.interfaces.IDataManagerSavepoint)
class NoOpSavepoint:
    def rollback(self):
        raise RuntimeError('Cannot rollback BC-API savepoints.')
