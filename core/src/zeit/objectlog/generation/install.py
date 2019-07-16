
import zeit.objectlog.interfaces
import zeit.objectlog.objectlog
import zope.component
import zope.component.hooks
import zope.app.zopeappgenerations


def install(root):
    site_manager = zope.component.getSiteManager()
    site_manager['objectlog'] = log = zeit.objectlog.objectlog.ObjectLog()
    site_manager.registerUtility(
        log, zeit.objectlog.interfaces.IObjectLog)


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.component.hooks.setSite(root)
        install(root)
    finally:
        zope.component.hooks.setSite(site)
