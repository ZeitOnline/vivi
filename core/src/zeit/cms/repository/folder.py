# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import zope.interface

import zeit.connector.interfaces
import zeit.connector.resource

import zeit.cms.repository.repository
import zeit.cms.repository.interfaces


class Folder(zeit.cms.repository.repository.Container):
    """The Folder structrues content in the repository."""

    zope.interface.implements(zeit.cms.repository.interfaces.IFolder)


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def folderFactory(context):
    folder = Folder()
    folder.uniqueId = context.id
    return folder


@zope.interface.implementer(zeit.connector.interfaces.IResource)
@zope.component.adapter(zeit.cms.repository.interfaces.IFolder)
def folderToResource(context):
    try:
        properties = zeit.connector.interfaces.IWebDAVReadProperties(
            context)
    except TypeError:
        properties = zeit.connector.resource.WebDAVProperties()
    return zeit.connector.resource.Resource(
        context.uniqueId, context.__name__, 'collection',
        data=StringIO.StringIO(),
        contentType='httpd/unix-directory',
        properties=properties)
