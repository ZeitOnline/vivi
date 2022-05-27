from zeit.content.image.transform import THUMBNAIL_FOLDER_NAME
import grokcore.component as grok
import zeit.content.gallery.interfaces
import zeit.workflow.dependency


class PublicationDependencies(zeit.workflow.dependency.DependencyBase):
    """Gallery dependencies."""

    grok.context(zeit.content.gallery.interfaces.IGallery)
    grok.name('zeit.content.gallery.image_folder')

    retract_dependencies = True

    def get_dependencies(self):
        folder = self.context.image_folder
        if folder is not None:
            return [x for x in folder.values()
                    if x.__name__ != THUMBNAIL_FOLDER_NAME]
        return ()
