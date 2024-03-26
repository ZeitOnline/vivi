import zope.component
import zope.component.hooks
import zope.generations.utility

import zeit.connector.invalidator


def update(root):
    """Removes obsolete invalidator utility"""
    sm = zope.component.getSiteManager()
    sm.unregisterUtility(sm['connector-invalidator'], zeit.connector.invalidator.IInvalidator)
    del sm['connector-invalidator']


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        update(root)
    finally:
        zope.component.hooks.setSite(site)
