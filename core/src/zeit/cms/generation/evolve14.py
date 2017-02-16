from lovely.remotetask.interfaces import ITaskService
import zeit.cms.generation
import zeit.cms.generation.install
import zope.component


def update(root):
    site_manager = zope.component.getSiteManager()
    for name, _ in site_manager.getUtilitiesFor(ITaskService):
        done = site_manager.unregisterUtility(provided=ITaskService, name=name)
        if not done:
            raise RuntimeError('unregisterUtility did not return True')


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
