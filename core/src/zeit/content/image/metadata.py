# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify

import zope.component
import zope.interface

import zeit.cms.content.dav
import zeit.cms.content.interfaces

import zeit.content.image.interfaces


class ImageMetadata(object):

    zope.interface.implements(zeit.content.image.interfaces.IImageMetadata)

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/image',
        ('expires', 'alt', 'caption', 'links_to'))
    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/document',
        ('title', 'year', 'volume', 'copyrights'))

    def __init__(self, context):
        self.context = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
@zope.component.adapter(ImageMetadata)
def metadata_webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(
        context.context)


@zope.component.adapter(zeit.content.image.interfaces.IImageMetadata)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def MetadataXMLReference(context):
    """XML representation of image."""

    attributes = {}
    def set_if_not_empty(name, value):
        if value:
            attributes[name] = value

    copyrights = []
    for text, link in context.copyrights:
        node = lxml.objectify.E.copyright(text)
        if link:
            node.set('link', link)
        copyrights.append(node)

    expires = context.expires
    if expires:
        expires = expires.isoformat()
        attributes['expires'] = expires

    set_if_not_empty('title', context.caption)
    set_if_not_empty('alt', context.alt)
    set_if_not_empty('href', context.links_to)

    image = lxml.objectify.E.image(
        lxml.objectify.E.bu(context.alt),
        *copyrights,
        **attributes)
    return image
