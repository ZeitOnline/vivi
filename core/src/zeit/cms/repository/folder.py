import grokcore.component as grok
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.type
import zeit.cms.util
import zeit.cms.workflow.dependency


@zope.interface.implementer(zeit.cms.repository.interfaces.IFolder)
class Folder(zeit.cms.repository.repository.Container):
    """The Folder structures content in the repository."""


class FolderType(zeit.cms.type.TypeDeclaration):
    interface = zeit.cms.repository.interfaces.IFolder
    type = 'collection'
    title = _('Folder')
    addform = 'zeit.cms.repository.folder.Add'
    factory = Folder
    resource_is_collection = True

    def content(self, resource):
        folder = self.factory()
        folder.uniqueId = resource.id
        return folder

    def resource_body(self, content):
        return zeit.cms.util.MemoryFile()


@zope.interface.implementer(zeit.cms.content.interfaces.IContentSortKey)
@zope.component.adapter(zeit.cms.repository.interfaces.IFolder)
def folder_sort_key(context):
    weight = -5  # folders first
    key = context.__name__.lower()
    return (weight, key)


class FolderDependencies(zeit.cms.workflow.dependency.DependencyBase):
    grok.context(zeit.cms.repository.interfaces.ICollection)
    grok.name('zeit.cms.repository.folder')

    retract_dependencies = True

    def get_dependencies(self):
        return self.context.values()
