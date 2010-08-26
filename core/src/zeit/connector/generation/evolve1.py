# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

generation = 1


import zeit.connector.generation.install
import zeit.connector.interfaces
import zeit.connector.lockinfo
import zope.app.component
import zope.app.component.hooks
import zope.app.zopeappgenerations


def update(root):
    site_manager = zope.component.getSiteManager()
    # Install lockinfo and move the storage from the body cache
    lockinfo = zeit.connector.generation.install.installLocalUtility(
        site_manager, zeit.connector.lockinfo.LockInfo,
        'connector-lockinfo',
        zeit.connector.interfaces.ILockInfoStorage)

    body_cache = site_manager['connector-body-cache']
    lockinfo._storage = body_cache.locktokens
    del body_cache.locktokens


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        update(root)
    finally:
        zope.app.component.hooks.setSite(site)

