import grokcore.component as grok
import zeit.cms.interfaces
import zeit.workflow.interfaces
import zope.component


class Dependencies(grok.Adapter):
    """Adapter to find the publication dependencies of an object."""

    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(zeit.workflow.interfaces.IPublicationDependencies)

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
