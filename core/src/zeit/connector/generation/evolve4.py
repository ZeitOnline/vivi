import zope.component
import zope.component.hooks
import zope.app.zopeappgenerations


def update(root):
    """Remove cruft data."""

    site_manager = zope.component.getSiteManager()

    body_cache = site_manager['connector-body-cache']
    try:
        del body_cache._time_to_id
    except AttributeError:
        pass


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.component.hooks.setSite(root)
        update(root)
    finally:
        zope.component.hooks.setSite(site)
