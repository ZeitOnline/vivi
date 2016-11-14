import zeit.cms.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.interface


class Dependencies(object):
    """Adapter to find the publication dependencies of an object."""

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        dependencies = set()
        for name, this_deps in zope.component.getAdapters(
                (self.context,),
                zeit.workflow.interfaces.IPublicationDependencies):
            if not name:
                # This is actually this adapter
                continue
            dependencies.update(this_deps.get_dependencies())
        return sorted(dependencies, key=lambda x: x.uniqueId)
