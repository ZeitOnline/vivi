class NoopDatamanager:
    """Datamanager which does nothing."""

    def abort(self, trans):
        pass

    def commit(self, trans):
        pass

    def tpc_begin(self, trans):
        pass

    def tpc_abort(self, trans):
        pass

    def sortKey(self):
        return 'anything'


class CommitExceptionDataManager(NoopDatamanager):
    """DataManager which raises an exception in tpc_vote."""

    def __init__(self, error):
        self.error = error

    def tpc_vote(self, trans):
        raise self.error
