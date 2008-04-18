# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.component.hooks
import zope.app.component
import zope.app.zopeappgenerations

import zeit.objectlog.interfaces
import zeit.objectlog.objectlog

def install(root):
    site_manager = zope.component.getSiteManager()
    site_manager['objectlog'] = log = zeit.objectlog.objectlog.ObjectLog()
    site_manager.registerUtility(
        log, zeit.objectlog.interfaces.IObjectLog)


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        install(root)
    finally:
        zope.app.component.hooks.setSite(site)
