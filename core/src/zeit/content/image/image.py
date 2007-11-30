# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import lxml.objectify
import gocept.lxml.interfaces

import zope.component
import zope.interface

import zope.app.container.contained
import zope.app.file.image

import zeit.cms.connector
import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.cms.content.util
import zeit.xmleditor.interfaces

import zeit.content.image.interfaces


class Image(zope.app.file.image.Image,
            zope.app.container.contained.Contained):
    """Image contanis exactly one image."""

    zope.interface.implements(zeit.content.image.interfaces.IImage)

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImage,
        'http://namespaces.zeit.de/CMS/image',
        ('expires', 'alt', 'caption'))
    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImage,
        'http://namespaces.zeit.de/CMS/document',
        ('title', 'year', 'volume', 'copyrights'))

    def __init__(self, __name__=None, **data):
        self.uniqueId = None
        self.__name__ = __name__
        zeit.cms.content.util.applySchemaData(
            self, zeit.content.image.interfaces.IImageSchema, data)


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def imageFactory(context):
    # TODO: we really should use a blob for the data
    image = Image(data=context.data,
                  contentType=context.contentType)
    zeit.cms.interfaces.IWebDAVProperties(image).update(context.properties)
    return image


@zope.interface.implementer(zeit.cms.interfaces.IResource)
@zope.component.adapter(zeit.content.image.interfaces.IImage)
def resourceFactory(context):
    return zeit.cms.connector.Resource(
        context.uniqueId, context.__name__, 'image',
        data=StringIO.StringIO(context.data),
        contentType=context.contentType,
        properties=zeit.cms.interfaces.IWebDAVProperties(context))


class XMLReference(object):

    zope.component.adapts(zeit.content.image.interfaces.IImage)
    zope.interface.implements(zeit.xmleditor.interfaces.IXMLReference)

    def __init__(self, context):
        self.context = context

    @property
    def xml(self):
        image = lxml.objectify.XML('<image/>')
        image.set('src', self.context.uniqueId)
        image.set('expires', unicode(self.context.expires))
        image.set('alt', unicode(self.context.alt))
        image.set('title', unicode(self.context.caption))
        image.copyright = self.context.copyrights
        return image


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(gocept.lxml.interfaces.IObjectified)
def image_objectified(context):
    return zeit.xmleditor.interfaces.IXMLReference(context).xml
