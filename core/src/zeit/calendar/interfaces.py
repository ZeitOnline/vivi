# vim: fileencoding=utf8 encoding=utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

# Inspired by schooltool.

import zope.interface
import zope.schema

import zope.app.container.interfaces

import zeit.cms.interfaces
import zeit.cms.content.contentsource
from zeit.cms.i18n import MessageFactory as _



class ICalendarEvent(zope.interface.Interface):
    """An event."""

    start = zope.schema.Date(
        title=_("Start"),
        description=_("Date when the event starts."))

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Title will be shown in overview pages."))

    description = zope.schema.Text(
        title=_("Description"),
        required=False)

    related = zope.schema.Tuple(
        title=_("Related content"),
        description=_("Documents that are related to this object."),
        default=(),
        required=False,
        value_type=zope.schema.Choice(
            source=zeit.cms.content.contentsource.cmsContentSource))

    location = zope.schema.TextLine(
        title=_("Location/Type"),
        description=_("Where should the article be placed."),
        required=False)

    thema = zope.schema.Bool(
        title=_("Topic?"),
        description=_("Is the article a topic for the next week?"))


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
