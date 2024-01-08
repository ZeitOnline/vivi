import BTrees
import zope.app.zopeappgenerations
import zope.component
import zope.component.hooks


def install(root):
    # Migrate from one central time line to one per object
    site_manager = zope.component.getSiteManager()
    log = site_manager['objectlog']
    for key in log._object_log:
        # Iterate over the objects
        new_log = BTrees.family64.IO.BTree()
        for time_key in log._object_log[key]:
            # Iterate over timeline entries per object
            new_log[time_key] = log._time_line[time_key]
        log._object_log[key] = new_log

    del log._time_line


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.component.hooks.setSite(root)
        install(root)
    finally:
        zope.component.hooks.setSite(site)
