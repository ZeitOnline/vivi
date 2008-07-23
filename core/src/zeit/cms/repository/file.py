# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""File objects."""

import ZODB.blob
import persistent

import zope.app.container.contained
import zope.component
import zope.interface
import zope.security.proxy

import zeit.cms.workingcopy.interfaces
import zeit.connector.interfaces
import zeit.cms.repository.interfaces


class RepositoryFile(zope.app.container.contained.Contained):
    """A file in the repository."""

    zope.interface.implements(zeit.cms.repository.interfaces.IFile)

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


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def repositoryfile_factory(context):
    return RepositoryFile(context.id, context.contentType)


class LocalFile(persistent.Persistent, RepositoryFile):
    """A file which also stores local data."""

    zope.interface.implements(zeit.cms.workingcopy.interfaces.ILocalContent)

    local_data = None
    BLOCK_SIZE = 10240

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
                data = super(LocalFile, self).open()
                return data
            self.local_data = ZODB.blob.Blob()

        return self.local_data.open(mode)


@zope.component.adapter(RepositoryFile)
@zope.interface.implementer(zeit.cms.workingcopy.interfaces.ILocalContent)
def localfile_factory(context):
    f = LocalFile(context.uniqueId, context.mimeType)
    f.__name__ = context.__name__
    return f


@zope.component.adapter(zeit.cms.repository.interfaces.IFile)
@zope.interface.implementer(zeit.connector.interfaces.IResource)
def resource_factory(context):
    return zeit.cms.connector.Resource(
        context.uniqueId, context.__name__, 'file',
        zope.security.proxy.removeSecurityProxy(context.open('r')),
        contentType=context.mimeType,
        properties=zeit.cms.interfaces.IWebDAVProperties(context))
