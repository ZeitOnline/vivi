from zeit.cms.i18n import MessageFactory as _
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.content.dynamicfolder.interfaces
import zope.interface


class DynamicFolder(zeit.cms.repository.folder.Folder):

    zope.interface.implements(
        zeit.content.dynamicfolder.interfaces.IDynamicFolder)


class DynamicFolderType(zeit.cms.repository.folder.FolderType):

    factory = DynamicFolder
    interface = zeit.content.dynamicfolder.interfaces.IDynamicFolder
    type = 'dynamic-collection'
    title = _('Dynamic Folder')
    addform = zeit.cms.type.SKIP_ADD
