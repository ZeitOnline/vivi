import zope.component
import zope.component.hooks
import zope.generations.utility


def update(root):
    import zeit.connector.invalidator

    site_manager = zope.component.getSiteManager()
    zeit.connector.generation.install.installLocalUtility(
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
        update(root)
    finally:
        zope.component.hooks.setSite(site)
