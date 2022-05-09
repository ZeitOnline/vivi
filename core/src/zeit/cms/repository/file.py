from zeit.cms.i18n import MessageFactory as _
import ZODB.blob
import persistent
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.type
import zeit.cms.workingcopy.interfaces
import zeit.connector.interfaces
import zope.component
import zope.interface
import zope.security.proxy


@zope.interface.implementer(
    zeit.cms.repository.interfaces.IFile,
    zeit.cms.interfaces.IAsset)
class RepositoryFile(zeit.cms.repository.repository.ContentBase):
    """A file in the repository."""

    def __init__(self, uniqueId, mimeType):
        super().__init__()
        self.uniqueId = uniqueId
        self.parameters = {}
        self.mimeType = mimeType

    def open(self, mode='r'):
        if mode != 'r':
            raise ValueError(mode)
        return self.connector[self.uniqueId].data

    def openDetached(self):
        return self.open()

    @property
    def size(self):
        f = self.open()
        f.seek(0, 2)
        return f.tell()

    @property
    def connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)


@zope.interface.implementer(zeit.cms.workingcopy.interfaces.ILocalContent)
class LocalFile(persistent.Persistent, RepositoryFile):
    """A file which also stores local data."""

    local_data = None

    def __init__(self, uniqueId=None, mimeType=''):
        super().__init__(uniqueId, mimeType)

    def open(self, mode='r'):
        if mode not in ('r', 'w'):
            raise ValueError(mode)

        if not self.uniqueId and self.local_data is None and mode == 'r':
            raise ValueError("Cannot open for reading, no data available.")

        if self.local_data is None:
            if mode == 'r':
                try:
                    data = super().open()
                except KeyError:
                    pass
                else:
                    return data
            self.local_data = ZODB.blob.Blob()

        return self.local_data.open(mode)


@zope.component.adapter(RepositoryFile)
@zope.interface.implementer(zeit.cms.workingcopy.interfaces.ILocalContent)
def localfile_factory(context):
    f = LocalFile(context.uniqueId, context.mimeType)
    f.__name__ = context.__name__
    return f


class FileType(zeit.cms.type.TypeDeclaration):

    interface = zeit.cms.repository.interfaces.IFile
    type = 'file'
    title = _('File')
    addform = 'zeit.cms.repository.file.Add'
    factory = RepositoryFile

    def content(self, resource):
        return self.factory(resource.id, resource.contentType)

    def resource_body(self, content):
        return zope.security.proxy.removeSecurityProxy(content.open('r'))

    def resource_content_type(self, content):
        return content.mimeType
