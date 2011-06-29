# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import StringIO
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.type
import zeit.connector.interfaces
import zeit.connector.resource
import zope.interface


class Folder(zeit.cms.repository.repository.Container):
    """The Folder structures content in the repository."""

    zope.interface.implements(zeit.cms.repository.interfaces.IFolder)



class FolderType(zeit.cms.type.TypeDeclaration):

    interface = zeit.cms.repository.interfaces.IFolder
    type = 'collection'
    title = _('Folder')
    addform = 'zeit.cms.repository.folder.Add'
    factory = Folder

    def content(self, resource):
        folder = self.factory()
        folder.uniqueId = resource.id
        return folder

    def resource_body(self, content):
        return StringIO.StringIO()

    def resource_content_type(self, content):
        return 'httpd/unix-directory'


@zope.interface.implementer(zeit.cms.content.interfaces.IContentSortKey)
@zope.component.adapter(zeit.cms.repository.interfaces.IFolder)
def folder_sort_key(context):
    weight = -5  # folders first

    if context.__name__ == 'online':
        # online first
        weight = -6
    try:
        key = -int(context.__name__)
    except ValueError:
        key = context.__name__.lower()

    return (weight, key)
