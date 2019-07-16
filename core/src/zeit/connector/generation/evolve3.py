import BTrees
import zope.component
import zope.component.hooks
import zope.app.zopeappgenerations


def update(root):
    """Migrate to the set oriented last access counter."""

    site_manager = zope.component.getSiteManager()

    body_cache = site_manager['connector-body-cache']
    body_cache._access_time_to_ids = BTrees.family32.IO.BTree()
    for id in body_cache._time_to_id.values():
        body_cache._update_cache_access(id)


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.component.hooks.setSite(root)
        update(root)
    finally:
        zope.component.hooks.setSite(site)
