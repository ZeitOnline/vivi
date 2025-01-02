import zope.component

import zeit.cms.generation


def update(root):
    from zeit.ldap.azure import ITokenCache

    registry = zope.component.getSiteManager()
    utility = registry.getUtility(ITokenCache)
    registry.unregisterUtility(utility, ITokenCache)
    del registry['azure-token-cache']


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
