# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import lxml.objectify
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.interface
import zope.schema


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

    zeit.cms.content.dav.mapProperties(
        zeit.content.image.interfaces.IImageMetadata,
        'http://namespaces.zeit.de/CMS/meta',
        ('acquire_metadata',))

    def __init__(self, context):
        self.context = context


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
@zope.component.adapter(ImageMetadata)
def metadata_webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(
        context.context)


@grokcore.component.implementer(zeit.content.image.interfaces.IImageMetadata)
@grokcore.component.adapter(zeit.content.image.interfaces.IImage)
def metadata_for_image(image):
    metadata = ImageMetadata(image)
    # Be sure to get the image in the repository
    parent = None
    if image.uniqueId:
        image_in_repository = parent = zeit.cms.interfaces.ICMSContent(
            image.uniqueId, None)
        if image_in_repository is not None:
            parent = image_in_repository.__parent__
    if zeit.content.image.interfaces.IImageGroup.providedBy(parent):
        # The image *is* in an image group.
        if metadata.acquire_metadata is None or metadata.acquire_metadata:
            group_metadata = zeit.content.image.interfaces.IImageMetadata(
                parent)
            if zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(image):
                for name, field in zope.schema.getFieldsInOrder(
                    zeit.content.image.interfaces.IImageMetadata):
                    value = getattr(group_metadata, name, None)
                    setattr(metadata, name, value)
                metadata.acquire_metadata = False
            else:
                # For repository content return the metadata of the group.
                metadata = group_metadata

    return metadata


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

    caption = lxml.objectify.E.bu(context.caption or None)

    image = lxml.objectify.E.image(
        caption,
        *copyrights,
        **attributes)

    return image
