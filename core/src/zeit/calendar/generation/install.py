# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.zopeappgenerations

import zeit.cms.generation.install

import zeit.calendar.calendar
import zeit.calendar.interfaces


def install(root):
    zeit.cms.generation.install.installLocalUtility(
        root, zeit.calendar.calendar.Calendar,
        'calendar', zeit.calendar.interfaces.ICalendar)


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        install(root)
    finally:
        zope.app.component.hooks.setSite(site)
