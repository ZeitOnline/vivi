# vim: fileencoding=utf8 encoding=utf8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

# Inspired by schooltool.

import zope.interface
import zope.schema

import zope.app.container.interfaces

import zeit.cms.interfaces


class ICalendarEvent(zope.interface.Interface):
    """An event."""

    start = zope.schema.Date(
        title=u"Start",
        description=u"Date when the event starts.")

    title = zope.schema.TextLine(
        title=u"Title",
        description=u"Title will be shown in overview pages.")

    description = zope.schema.Text(
        title=u"Description",
        required=False)

    related = zope.schema.Tuple(
        title=u"Related documents",
        description=u"Documents that are related to this event.",
        default=(),
        required=False,
        value_type=zope.schema.Object(zeit.cms.interfaces.ICMSContent))

    location = zope.schema.TextLine(
        title=u"Location/Typ",
        description=u"Wo soll der Artikel erscheinen?",
        required=False)

    thema = zope.schema.Bool(
        title=u"Thema?",
        description=u"Ist der Artikel ggf. ein Thema für die Nächste Woche?")


class ICalendar(zope.app.container.interfaces.IReadContainer):
    """Calendar."""

    def getEvents(date):
        """Return the events occuring on `date`.

        date: datetime.date object.

        """

    def haveEvents(date):
        """Return if there are events occuring on `date`.

        date: datetime.date object.

        """


class IEditCalendar(zope.app.container.interfaces.IWriteContainer):
    pass
