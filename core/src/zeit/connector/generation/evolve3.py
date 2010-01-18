# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Migrate to the set oriented last access counter."""

import BTrees
import zope.app.component.hooks
import zope.app.component
import zope.app.zopeappgenerations


def update(root):
    site_manager = zope.component.getSiteManager()

    body_cache = site_manager['connector-body-cache']
    body_cache._access_time_to_ids = BTrees.family32.IO.BTree()
    for id in body_cache._time_to_id.values():
        body_cache._update_cache_access(id)


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        update(root)
    finally:
        zope.app.component.hooks.setSite(site)

