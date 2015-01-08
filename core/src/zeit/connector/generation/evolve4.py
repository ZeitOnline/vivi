import zope.app.component.hooks
import zope.app.component
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
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        update(root)
    finally:
        zope.app.component.hooks.setSite(site)
