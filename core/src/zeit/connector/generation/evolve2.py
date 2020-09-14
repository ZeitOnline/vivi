import zope.component
import zope.component.hooks
import zope.generations.utility


generation = 1


def update(root):
    site_manager = zope.component.getSiteManager()

    # Clear body cache because we have completely different cache keys now.
    body_cache = site_manager['connector-body-cache']
    body_cache._last_access_time.clear()
    body_cache._time_to_id.clear()
    body_cache._data.clear()
    body_cache._etags.clear()


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        update(root)
    finally:
        zope.component.hooks.setSite(site)
