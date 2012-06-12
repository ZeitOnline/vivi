# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.objectlog.i18n import MessageFactory as _
import BTrees
import datetime
import logging
import persistent
import pytz
import time
import transaction
import zeit.objectlog.interfaces
import zope.app.keyreference.interfaces
import zope.component
import zope.interface
import zope.security.management


logger = logging.getLogger(__name__)


class ObjectLog(persistent.Persistent):
    """Object log."""

    zope.interface.implements(zeit.objectlog.interfaces.IObjectLog)

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

    def log(self, object, message, mapping=None, timestamp=None):
        logger.debug("Logging: %s %s %s" % (object, message, mapping))
        obj_key = zope.app.keyreference.interfaces.IKeyReference(object)

        object_log = self._object_log.get(obj_key)
        if object_log is None:
            # Create a timeline for the object.
            object_log = self._object_log[obj_key] = BTrees.family64.IO.BTree()

        log_entry = LogEntry(object, message, mapping, timestamp)

        time_key = int(time.mktime(log_entry.time.utctimetuple()) * 10e6)
        while not object_log.insert(time_key, log_entry):
            time_key += 1

        # Create savepoint to assign oid to log-entries. Required for
        # displaying in the same transaction.
        transaction.savepoint(optimistic=True)

    def clean(self, timedelta):
        reference_time = int((time.time()
                              - timedelta.days * 3600 * 24
                              - timedelta.seconds)
                             * 10e6)
        remove = []
        for key in self._object_log:
            log = self._object_log[key]
            for time_key in list(log.keys(max=reference_time)):
                del log[time_key]
            if not log:
                remove.append(key)
        for key in remove:
            del self._object_log[key]


class LogEntry(persistent.Persistent):

    zope.interface.implements(zeit.objectlog.interfaces.ILogEntry)

    def __init__(self, object, message, mapping, timestamp):
        self.time = timestamp or datetime.datetime.now(pytz.UTC)
        self.object_reference = zope.app.keyreference.interfaces.IKeyReference(
            object)
        self.message = message
        self.mapping = mapping
        participations = (zope.security.management.getInteraction()
                          .participations)
        if participations and participations[0].principal:
            self.principal = participations[0].principal.id
        else:
            self.principal = None

    def get_object(self):
        return self.object_reference()


class Log(object):

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(zeit.objectlog.interfaces.ILog)

    def __init__(self, context):
        self.context = context

    def log(self, message, mapping=None, timestamp=None):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(self.context, message, mapping, timestamp)

    def get_log(self):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        return log.get_log(self.context)

    @property
    def logs(self):
        entries = self.get_log()
        processor = zeit.objectlog.interfaces.ILogProcessor(self.context,
                                                            None)
        if processor is not None:
            entries = processor(entries)
        return tuple(reversed(tuple(entries)))
