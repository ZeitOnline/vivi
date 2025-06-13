import zope.component

import zeit.cms.generation


def update(root):
    from zeit.cms.content.interfaces import ITemplateManager

    registry = zope.component.getSiteManager()
    for name, utility in registry.getUtilitiesFor(ITemplateManager):
        registry.unregisterUtility(utility, ITemplateManager, name)
        del utility.__parent__[utility.__name__]


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
