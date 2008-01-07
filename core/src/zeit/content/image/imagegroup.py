# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.repository.repository
import zeit.connector.resource

import zeit.content.image.interfaces


class ImageGroup(zeit.cms.repository.repository.Container):

    zope.interface.implements(zeit.content.image.interfaces.IImageGroup)



@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def imageGroupFactory(context):
    ig = ImageGroup()
    ig.uniqueId = context.id
    return ig


@zope.interface.implementer(zeit.connector.interfaces.IResource)
@zope.component.adapter(zeit.content.image.interfaces.IImageGroup)
def imageGroupToResource(context):
    try:
        properties = zeit.connector.interfaces.IWebDAVReadProperties(
            context)
    except TypeError:
        properties = zeit.connector.resource.WebDAVProperties()
    return zeit.connector.resource.Resource(
        context.uniqueId, context.__name__, 'image-group',
        data=StringIO.StringIO(),
        contentType='httpd/unix-directory',
        properties=properties)
