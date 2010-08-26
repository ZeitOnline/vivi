# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Remove cruft data."""

import zope.app.component.hooks
import zope.app.component
import zope.app.zopeappgenerations


def update(root):
    site_manager = zope.component.getSiteManager()

    body_cache = site_manager['connector-body-cache']
    try:
        del body_cache._time_to_id
    except AttributeError:
        pass


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        update(root)
    finally:
        zope.app.component.hooks.setSite(site)

