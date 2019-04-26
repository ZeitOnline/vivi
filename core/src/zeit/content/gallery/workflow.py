import grokcore.component as grok
import zeit.content.gallery.interfaces
import zeit.workflow.dependency


class PublicationDependencies(zeit.workflow.dependency.DependencyBase):
    """Gallery dependencies."""

    grok.context(zeit.content.gallery.interfaces.IGallery)
    grok.name('zeit.content.gallery.image_folder')

    retract_dependencies = True

    def get_dependencies(self):
        if self.context.image_folder is not None:
            return (self.context.image_folder,)
        return ()
