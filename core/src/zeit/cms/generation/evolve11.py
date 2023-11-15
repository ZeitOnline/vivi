import zeit.cms.generation
import zeit.cms.generation.install
import zope.component
import zope.error.interfaces


def update(root):
    current = zope.component.getUtility(zope.error.interfaces.IErrorReportingUtility)
    zope.component.getSiteManager().unregisterUtility(
        current, zope.error.interfaces.IErrorReportingUtility
    )
    del current.__parent__[current.__name__]
    zeit.cms.generation.install.installErrorReportingUtility(root)


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
