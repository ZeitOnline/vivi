import BTrees
import zope.component
import zope.component.hooks
import zope.generations.utility

import zeit.connector.cache
import zeit.connector.interfaces


def update(root):
    """Adds access time to property and child name cache."""
    ifaces = [zeit.connector.interfaces.IPropertyCache, zeit.connector.interfaces.IChildNameCache]
    for iface in ifaces:
        cache = zope.component.getUtility(iface)
        zeit.connector.cache.AccessTimes.__init__(cache)
        cache._access_time_to_ids[0] = BTrees.family32.OI.TreeSet()


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        update(root)
    finally:
        zope.component.hooks.setSite(site)
