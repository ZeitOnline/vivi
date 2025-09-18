import BTrees
import zope.component

import zeit.objectlog.generation


def update(root):
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
    zeit.objectlog.generation.do_evolve(context, update)
