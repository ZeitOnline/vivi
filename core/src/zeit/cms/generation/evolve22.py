from zope.error.interfaces import IErrorReportingUtility
import zope.component

import zeit.cms.generation


def update(root):
    registry = zope.component.getSiteManager()
    utility = registry.getUtility(IErrorReportingUtility)
    registry.unregisterUtility(utility, IErrorReportingUtility)
    del utility.__parent__[utility.__name__]


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
