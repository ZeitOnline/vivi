import zeit.connector.interfaces
import zope.app.zopeappgenerations
import zope.component
import zope.component.hooks


def update(root):
    """Removes obsolete lockinfo cache"""
    sm = zope.component.getSiteManager()
    sm.unregisterUtility(
        sm['connector-lockinfo'],
        zeit.connector.interfaces.ILockInfoStorage)
    del sm['connector-lockinfo']


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.component.hooks.setSite(root)
        update(root)
    finally:
        zope.component.hooks.setSite(site)
