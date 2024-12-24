import zope.component

import zeit.cms.generation


def update(root):
    from zeit.cms.relation.interfaces import IRelations

    registry = zope.component.getSiteManager()
    utility = registry.getUtility(IRelations)
    registry.unregisterUtility(utility, IRelations)
    del registry['relations']


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
