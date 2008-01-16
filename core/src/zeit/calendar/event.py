# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent

import zope.interface

import zope.app.container.contained

import zeit.cms.content.util

import zeit.calendar.interfaces


class Event(persistent.Persistent,
            zope.app.container.contained.Contained):

    zope.interface.implements(zeit.calendar.interfaces.ICalendarEvent)

    def __init__(self, **kwargs):
        zeit.cms.content.util.applySchemaData(
            self,
            zeit.calendar.interfaces.ICalendarEvent,
            kwargs)
