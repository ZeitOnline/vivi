import zope.component
import zope.component.hooks
import zope.generations.utility

import zeit.connector.cache
import zeit.connector.interfaces
import zeit.connector.invalidator


def installLocalUtility(root, factory, name, interface, utility_name=''):
    utility = factory()
    root[name] = utility
    site_manager = zope.component.getSiteManager()
    site_manager.registerUtility(utility, interface, name=utility_name)
    return root[name]


def install(root):
    site_manager = zope.component.getSiteManager()
    installLocalUtility(
        site_manager,
        zeit.connector.cache.ResourceCache,
        'connector-body-cache',
        zeit.connector.interfaces.IResourceCache,
    )
    installLocalUtility(
        site_manager,
        zeit.connector.cache.PropertyCache,
        'connector-property-cache',
        zeit.connector.interfaces.IPropertyCache,
    )
    installLocalUtility(
        site_manager,
        zeit.connector.cache.ChildNameCache,
        'connector-child-name-cache',
        zeit.connector.interfaces.IChildNameCache,
    )
    installLocalUtility(
        site_manager,
        zeit.connector.invalidator.Invalidator,
        'connector-invalidator',
        zeit.connector.invalidator.IInvalidator,
    )


def evolve(context):
    site = zope.component.hooks.getSite()
    try:
        root = zope.generations.utility.getRootFolder(context)
        zope.component.hooks.setSite(root)
        install(root)
    finally:
        zope.component.hooks.setSite(site)
