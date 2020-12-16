import logging


def getState_with_logging(self, pickle):
    try:
        return self._old_getState(pickle)
    except Exception:
        log = logging.getLogger('ZODB.serialize')
        log.error('Unpickling error: %r', pickle)
