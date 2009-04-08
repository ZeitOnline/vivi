# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Remove cruft data."""

import zeit.connector.generation.install
import zeit.connector.invalidator
import zope.app.component
import zope.app.component.hooks
import zope.app.zopeappgenerations


def update(root):
    site_manager = zope.component.getSiteManager()
    zeit.connector.generation.install.installLocalUtility(
        site_manager, zeit.connector.invalidator.Invalidator,
        'connector-invalidator',
        zeit.connector.invalidator.IInvalidator)


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        update(root)
    finally:
        zope.app.component.hooks.setSite(site)

