========
Calendar
========

Events
======

Events are objects which can be added to the calendar. Let's create an event::

    >>> import datetime
    >>> from zeit.calendar.event import Event
    >>> event = Event(
    ...     start=datetime.date(2007, 6, 5),
    ...     title="Fotogalerie erstellen",
    ...     description="FG fuer Foo erstellen.")
    >>> event
    <zeit.calendar.event.Event object at 0x...>
    >>> event.start
    datetime.date(2007, 6, 5)
    >>> event.title
    'Fotogalerie erstellen'
    >>> event.description
    'FG fuer Foo erstellen.'


 XXX test object references / related

Calendar
========

The calendar is a container for events. Create a calendar. Initally it's empty::

    >>> import zope.interface.verify
    >>> from zeit.calendar.interfaces import ICalendar
    >>> from zeit.calendar.calendar import Calendar
    >>> zope.interface.verify.verifyClass(ICalendar, Calendar)
    True
    >>> calendar = Calendar()
    >>> calendar
    <zeit.calendar.calendar.Calendar object at 0x...>
    >>> len(calendar)
    0

    

Add the event to the calendar::

    >>> calendar['bla'] = event
    >>> len(calendar)
    1


We can get the event by date using the getEvents method::

    >>> date = datetime.date(2007, 6, 5)
    >>> events = list(calendar.getEvents(date))
    >>> events
    [<zeit.calendar.event.Event object at 0x...>]
    >>> events[0].title
    'Fotogalerie erstellen'
    >>> calendar.haveEvents(date)
    True


On other dates there are no events::

    >>> list(calendar.getEvents(datetime.date(2006, 6, 5)))
    []
    >>> calendar.haveEvents(datetime.date(2006, 6, 5))
    False
    >>> list(calendar.getEvents(datetime.date(2007, 6, 6)))
    []
    >>> list(calendar.getEvents(datetime.date(2007, 5, 6)))
    []


After removing the event from the calendar, it's also gone from getEvents::

    >>> del calendar['bla']
    >>> list(calendar.getEvents(date))
    []
    >>> calendar.haveEvents(date)
    False


Changing Calendar Events
========================

When chaning events the calendar index is updated automatically via a
subscriber to `ObjectModifiedEvent`.  So we add the event again::

    >>> calendar['ev'] = event
    >>> events = list(calendar.getEvents(datetime.date(2007, 6, 5)))
    >>> events
    [<zeit.calendar.event.Event object at 0x...>]

We change the start of the event. The index is not updated, yet::

    >>> event.start = datetime.date(2008, 10, 21)
    >>> list(calendar.getEvents(datetime.date(2007, 6, 5)))
    [<zeit.calendar.event.Event object at 0x...>]
    >>> list(calendar.getEvents(datetime.date(2008, 10, 21)))
    []

After updating the index, getEvent returns the result correctly again::

    >>> from zeit.calendar.calendar import updateIndexOnEventChange
    >>> updateIndexOnEventChange(event, object())
    >>> list(calendar.getEvents(datetime.date(2007, 6, 5)))
    []
    >>> list(calendar.getEvents(datetime.date(2008, 10, 21)))
    [<zeit.calendar.event.Event object at 0x...>]
