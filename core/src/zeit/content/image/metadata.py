# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.content.dav

import zeit.content.image.interfaces


class ImageMetadata(object):

    zope.interface.implements(zeit.content.image.interfaces.IImageMetadata)

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/image',
        ('expires', 'alt', 'caption'))
    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/document',
        ('title', 'year', 'volume', 'copyrights'))

    def __init__(self, context):
        self.context = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVReadProperties)
@zope.component.adapter(ImageMetadata)
def metadata_webdav_read_properties(context):
    return zeit.connector.interfaces.IWebDAVReadProperties(
        context.context)


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVWriteProperties)
@zope.component.adapter(ImageMetadata)
def metadata_webdav_write_properties(context):
    return zeit.connector.interfaces.IWebDAVWriteProperties(
        context.context)
