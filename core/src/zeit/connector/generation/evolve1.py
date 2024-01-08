import zope.component
import zope.component.hooks
import zope.generations.utility

import zeit.connector.generation.install
import zeit.connector.interfaces
import zeit.connector.lockinfo


generation = 1


def update(root):
    site_manager = zope.component.getSiteManager()
    # Install lockinfo and move the storage from the body cache
    lockinfo = zeit.connector.generation.install.installLocalUtility(
        site_manager,
        zeit.connector.lockinfo.LockInfo,
        'connector-lockinfo',
        zeit.connector.interfaces.ILockInfoStorage,
    )

    body_cache = site_manager['connector-body-cache']
    lockinfo._storage = body_cache.locktokens
    del body_cache.locktokens


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        update(root)
    finally:
        zope.component.hooks.setSite(site)
