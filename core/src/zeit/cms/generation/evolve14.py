from lovely.remotetask.interfaces import ITaskService
import zeit.cms.generation
import zeit.cms.generation.install
import zope.component


def update(root):
    site_manager = zope.component.getSiteManager()
    for name, service in site_manager.getUtilitiesFor(ITaskService):
        done = site_manager.unregisterUtility(provided=ITaskService, name=name)
        if not done:
            raise RuntimeError('unregisterUtility did not return True')
        del service.__parent__[service.__name__]


def evolve(context):
    """Remove the lovely.remotetask services."""
    zeit.cms.generation.do_evolve(context, update)
