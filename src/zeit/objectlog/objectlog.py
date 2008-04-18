# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime
import time

import BTrees
import persistent
import pytz

import zope.interface
import zope.security.management

import zope.app.keyreference.interfaces

import zeit.objectlog.interfaces


class ObjectLog(persistent.Persistent):
    """Object log."""

    zope.interface.implements(zeit.objectlog.interfaces.IObjectLog)

    def __init__(self):
        # Map *seconds* to log entry
        self._time_line = BTrees.family64.IO.BTree()
        # Map object to an object time line
        self._object_log = BTrees.family64.OO.BTree()

    def get_log(self, object):
        key = zope.app.keyreference.interfaces.IKeyReference(object)
        object_timeline = self._object_log.get(key, [])
        for time_key in sorted(object_timeline):
            yield self._time_line[time_key]

    def log(self, object, message, mapping=None):
        obj_key = zope.app.keyreference.interfaces.IKeyReference(object)

        log_entry = LogEntry(object, message, mapping)

        time_key = int(time.time() * 10e6)
        while not self._time_line.insert(time_key, log_entry):
            time_key += 1

        if obj_key not in self._object_log:
            # Create another timeline for the object itself.
            self._object_log[obj_key] = BTrees.family64.II.TreeSet()

        self._object_log[obj_key].insert(time_key)



class LogEntry(persistent.Persistent):

    zope.interface.implements(zeit.objectlog.interfaces.ILogEntry)

    def __init__(self, object, message, mapping):
        self.time = datetime.datetime.now(pytz.UTC)
        self.object_reference = zope.app.keyreference.interfaces.IKeyReference(
            object)
        self.message = message
        self.mapping = mapping
        participations = (zope.security.management.getInteraction()
                          .participations)
        if participations:
            self.principal = participations[0].principal.id
        else:
            self.principal = None

    def get_object(self):
        return self.object_reference()
