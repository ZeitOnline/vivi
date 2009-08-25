# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.objectify
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.interface


class ImageMetadata(object):

    zope.interface.implements(zeit.content.image.interfaces.IImageMetadata)

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        zeit.content.image.interfaces.IMAGE_NAMESPACE,
        ('alt', 'caption', 'links_to', 'alignment'))
    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/document',
        ('title', 'year', 'volume', 'copyrights'))
    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/document',
        ('copyrights',),
        use_default=True)

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

    set_if_not_empty('title', context.title)
    set_if_not_empty('alt', context.alt)
    set_if_not_empty('href', context.links_to)
    set_if_not_empty('align', context.alignment)

    # caption is an XMLSnippet. Parse it
    if context.caption:
        caption = lxml.objectify.fromstring('<bu>%s</bu>' % (context.caption,))
    else:
        caption = lxml.objectify.E.bu(None)

    image = lxml.objectify.E.image(
        caption,
        *copyrights,
        **attributes)

    return image
