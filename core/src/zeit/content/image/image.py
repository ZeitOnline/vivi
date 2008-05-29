# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import gocept.lxml.interfaces

import zope.component
import zope.interface

import zope.app.container.contained
import zope.app.file.image

import zeit.cms.connector
import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.cms.content.util
import zeit.cms.content.interfaces

import zeit.content.image.interfaces


class Image(zope.app.file.image.Image,
            zope.app.container.contained.Contained):
    """Image contanis exactly one image."""

    zope.interface.implements(zeit.content.image.interfaces.IImage)
    uniqueId = None


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def imageFactory(context):
    # TODO: we really should use a blob for the data
    image = Image()
    image.data = context.data
    if context.contentType:
        image.contentType = context.contentType
    return image


@zope.interface.implementer(zeit.cms.interfaces.IResource)
@zope.component.adapter(zeit.content.image.interfaces.IImage)
def resourceFactory(context):
    return zeit.cms.connector.Resource(
        context.uniqueId, context.__name__, 'image',
        data=StringIO.StringIO(context.data),
        contentType=context.contentType,
        properties=zeit.cms.interfaces.IWebDAVProperties(context))



@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    metadata = zeit.content.image.interfaces.IImageMetadata(context)
    image = zope.component.getAdapter(
        metadata,
        zeit.cms.content.interfaces.IXMLReference, name='image')
    image.set('src', context.uniqueId)
    if '.' in context.__name__:
        base, ext = context.__name__.rsplit('.', 1)
        image.set('type', ext)
    return image
