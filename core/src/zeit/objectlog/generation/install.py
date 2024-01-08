import zope.component
import zope.component.hooks
import zope.generations.utility

import zeit.objectlog.interfaces
import zeit.objectlog.objectlog


def install(root):
    site_manager = zope.component.getSiteManager()
    site_manager['objectlog'] = log = zeit.objectlog.objectlog.ObjectLog()
    site_manager.registerUtility(log, zeit.objectlog.interfaces.IObjectLog)


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        install(root)
    finally:
        zope.component.hooks.setSite(site)
