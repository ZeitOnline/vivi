# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees

import zope.app.component.hooks
import zope.app.component
import zope.app.zopeappgenerations

import zeit.objectlog.interfaces
import zeit.objectlog.objectlog


def install(root):
    # Migrate from one central time line to one per object
    site_manager = zope.component.getSiteManager()
    log = site_manager['objectlog']
    for key in log._object_log:
        # Iterate over the objects
        new_log = BTrees.family64.IO.BTree()
        for time_key in log._object_log[key]:
            # Iterate over timeline entries per object
            new_log[time_key] = log._time_line[time_key]
        log._object_log[key] = new_log

    del log._time_line

def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        install(root)
    finally:
        zope.app.component.hooks.setSite(site)
