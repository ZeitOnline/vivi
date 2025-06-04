import zope.component

import zeit.cms.generation


def update(root):
    from zeit.cms.content.interfaces import ITemplateManagerContainer

    registry = zope.component.getSiteManager()
    utility = registry.getUtility(ITemplateManagerContainer)
    registry.unregisterUtility(utility, ITemplateManagerContainer)
    del root['templates']


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
