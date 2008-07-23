# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import BTrees.OOBTree

import zope.component
import zope.interface
import zope.lifecycleevent
import zope.proxy

import zope.app.container.btree

import zeit.calendar.interfaces


class Calendar(zope.app.container.btree.BTreeContainer):

    zope.interface.implements(zeit.calendar.interfaces.ICalendar)

    def __init__(self):
        super(Calendar, self).__init__()
        self._date_index = BTrees.OOBTree.OOBTree()
        self._key_index = BTrees.OOBTree.OOBTree()

    def getEvents(self, date):
        """Return the events occuring on `date`."""
        for event_id in self._date_index.get(date, []):
            yield self[event_id]

    def haveEvents(self, date):
        """Return whether there are events occuring on `date`."""
        return bool(self._date_index.get(date))

    def __setitem__(self, key, value):
        event = zeit.calendar.interfaces.ICalendarEvent(value)
        super(Calendar, self).__setitem__(key, value)
        start = event.start
        self._index(start, key)

    def __delitem__(self, key):
        super(Calendar, self).__delitem__(key)
        self._unindex(key)

    def _index(self, day, key):
        if not isinstance(day, datetime.date):
            raise ValueError("Expected date object, got %r instead" % day)
        try:
            day_idx = self._date_index[day]
        except KeyError:
            self._date_index[day] = day_idx = BTrees.OOBTree.OOTreeSet()
        day_idx.insert(key)
        self._key_index[key] = day

    def _unindex(self, key):
        day = self._key_index[key]
        del self._key_index[key]
        self._date_index[day].remove(key)


@zope.component.adapter(
    zeit.calendar.interfaces.ICalendarEvent,
    zope.lifecycleevent.IObjectModifiedEvent)
def updateIndexOnEventChange(calendar_event, event):
    calendar = zope.proxy.removeAllProxies(calendar_event.__parent__)
    key = calendar_event.__name__
    calendar._unindex(key)
    calendar._index(calendar_event.start, key)
