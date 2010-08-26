# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

generation = 1


import zope.app.component
import zope.app.component.hooks
import zope.app.zopeappgenerations



def update(root):
    site_manager = zope.component.getSiteManager()

    # Clear body cache because we have completely different cache keys now.
    body_cache = site_manager['connector-body-cache']
    body_cache._last_access_time.clear()
    body_cache._time_to_id.clear()
    body_cache._data.clear()
    body_cache._etags.clear()


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        update(root)
    finally:
        zope.app.component.hooks.setSite(site)

