import argparse
import datetime
import logging
import time

import BTrees
import pendulum
import persistent
import transaction
import ZODB.POSException
import zope.app.keyreference.interfaces
import zope.component
import zope.interface
import zope.security.management

import zeit.cms.cli
import zeit.objectlog.interfaces


logger = logging.getLogger(__name__)


@zope.interface.implementer(zeit.objectlog.interfaces.IObjectLog)
class ObjectLog(persistent.Persistent):
    """Object log."""

    def __init__(self):
        # Map object to an object time line
        self._object_log = BTrees.family64.OO.BTree()

    def get_log(self, object):
        key = zope.app.keyreference.interfaces.IKeyReference(object, None)
        if key is None:
            return
        object_log = self._object_log.get(key, [])
        for key in object_log:
            yield object_log[key]

    def log(self, object, message):
        logger.debug('Logging: %s %s' % (object, message))
        obj_key = zope.app.keyreference.interfaces.IKeyReference(object)

        object_log = self._object_log.get(obj_key)
        if object_log is None:
            # Create a timeline for the object.
            object_log = self._object_log[obj_key] = BTrees.family64.IO.BTree()

        log_entry = LogEntry(object, message)

        time_key = int(time.mktime(log_entry.time.utctimetuple()) * 10e6)
        while not object_log.insert(time_key, log_entry):
            time_key += 1

        # Create savepoint to assign oid to log-entries. Required for
        # displaying in the same transaction.
        try:
            transaction.savepoint(optimistic=True)
        except Exception as e:
            e.add_note(
                'If you see this in a test you tried to run something '
                'asynchronously but inline of the process. Do not do this! '
                'Either run the test inline synchronously (default) or as actual '
                'end to end test using z3c.celery.layer.EndToEndLayer.'
            )
            raise e

    def move(self, source_ref, target):
        source_key = zope.app.keyreference.interfaces.IKeyReference(source_ref)
        log = self._object_log.pop(source_key, None)
        if log is None:
            return
        target_key = zope.app.keyreference.interfaces.IKeyReference(target)
        self._object_log[target_key] = log
        for entry in log.values():
            entry.object_reference = target_key

    def delete(self, object):
        key = zope.app.keyreference.interfaces.IKeyReference(object, None)
        if key is None:
            return
        self._object_log.pop(key, None)

    def clean(self, timedelta):
        reference_time = int(10e6 * (time.time() - timedelta.days * 3600 * 24 - timedelta.seconds))
        remove = []
        for key in self._object_log:
            log = self._object_log[key]
            try:
                for time_key in list(log.keys(max=reference_time)):
                    del log[time_key]
                if not log:
                    remove.append(key)
            except ZODB.POSException.POSKeyError:
                logger.warning('ZODB.POSException.POSKeyError, removing lost key %s', key)
                remove.append(key)
        for key in remove:
            del self._object_log[key]


@zope.interface.implementer(zeit.objectlog.interfaces.ILogEntry)
class LogEntry(persistent.Persistent):
    def __init__(self, object, message):
        self.time = pendulum.now('UTC')
        self.object_reference = zope.app.keyreference.interfaces.IKeyReference(object)
        self.message = message
        participations = zope.security.management.getInteraction().participations
        if participations and participations[0].principal:
            self.principal = participations[0].principal.id
        else:
            self.principal = None

    def get_object(self):
        return self.object_reference()


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zeit.objectlog.interfaces.ILog)
class Log:
    def __init__(self, context):
        self.context = context

    def log(self, message):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(self.context, message)

    def get_log(self):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        return log.get_log(self.context)

    @property
    def logs(self):
        entries = self.get_log()
        processor = zeit.objectlog.interfaces.ILogProcessor(self.context, None)
        if processor is not None:
            entries = processor(entries)
        return tuple(reversed(tuple(entries)))


@zeit.cms.cli.runner()
def clean():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=30)
    options = parser.parse_args()
    log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    logger.info('Cleaning objectlog, days=%s', options.days)
    for _ in zeit.cms.cli.commit_with_retry():
        log.clean(datetime.timedelta(days=options.days))
    logger.info('done')
