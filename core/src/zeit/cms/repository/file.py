# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""File objects."""

from zeit.cms.i18n import MessageFactory as _
import ZODB.blob
import persistent
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.cms.workingcopy.interfaces
import zeit.connector.interfaces
import zope.app.container.contained
import zope.component
import zope.interface
import zope.security.proxy


class RepositoryFile(zope.app.container.contained.Contained):
    """A file in the repository."""

    zope.interface.implements(zeit.cms.repository.interfaces.IFile,
                              zeit.cms.interfaces.IAsset)

    def __init__(self, uniqueId, mimeType):
        super(RepositoryFile, self).__init__()
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


class LocalFile(persistent.Persistent, RepositoryFile):
    """A file which also stores local data."""

    zope.interface.implements(zeit.cms.workingcopy.interfaces.ILocalContent)

    local_data = None

    def __init__(self, uniqueId=None, mimeType=''):
        super(LocalFile, self).__init__(uniqueId, mimeType)

    def open(self, mode='r'):
        if mode not in ('r', 'w'):
            raise ValueError(mode)

        if (not self.uniqueId
            and self.local_data is None
            and mode == 'r'):
            raise ValueError("Cannot open for reading, no data available.")

        if self.local_data is None:
            if mode == 'r':
                try:
                    data = super(LocalFile, self).open()
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

    def content(self, resource):
        return RepositoryFile(resource.id, resource.contentType)

    def resource_body(self, content):
        return zope.security.proxy.removeSecurityProxy(content.open('r'))

    def resource_content_type(self, content):
        return content.mimeType
