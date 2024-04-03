import zope.component
import zope.component.hooks
import zope.generations.utility

import zeit.push.interfaces


def update(root):
    """Removes obsolete Twitter credentials utility"""
    sm = zope.component.getSiteManager()
    sm.unregisterUtility(sm['twitter-credentials'], zeit.push.interfaces.ITwitterCredentials)
    del sm['twitter-credentials']


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        update(root)
    finally:
        zope.component.hooks.setSite(site)
