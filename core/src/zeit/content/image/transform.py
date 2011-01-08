# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image
import zeit.cms.repository.folder
import zeit.connector.interfaces
import zeit.content.image.interfaces
import zope.app.appsetup.product
import zope.component
import zope.interface
import zope.security.proxy


class ImageTransform(object):

    zope.interface.implements(zeit.content.image.interfaces.ITransform)
    zope.component.adapts(zeit.content.image.interfaces.IImage)

    def __init__(self, context):
        self.context = context
        try:
            self.image = PIL.Image.open(
                zope.security.proxy.removeSecurityProxy(context.open()))
            self.image.load()
        except IOError:
            raise zeit.content.image.interfaces.ImageProcessingError(
                "Cannot transform image %s" % context.__name__)

    def thumbnail(self, width, height, filter=PIL.Image.ANTIALIAS):
        image = self.image.copy()
        image.thumbnail((width, height), filter)
        return self._construct_image(image)

    def resize(self, width=None, height=None, filter=PIL.Image.ANTIALIAS):
        if width is None and height is None:
            raise TypeError('Need at least one of width and height.')

        orig_width, orig_height = self.image.size

        if width is None:
            width = orig_width * height / orig_height
        elif height is None:
            height = orig_height * width / orig_width

        image = self.image.resize((width, height), filter)
        return self._construct_image(image)

    def _construct_image(self, pil_image):

        image = zeit.content.image.image.LocalImage()
        image.mimeType = self.context.mimeType
        pil_image.save(image.open('w'), self.image.format)

        image.__parent__ = self.context
        image_times = zope.dublincore.interfaces.IDCTimes(self.context)
        if image_times.modified:
            thumb_times = zope.dublincore.interfaces.IDCTimes(image)
            thumb_times.modified = image_times.modified
        return image


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.content.image.interfaces.IPersistentThumbnail)
def persistent_thumbnail_factory(context):
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.image') or {}
    method_name = config.get('thumbnail-method', 'thumbnail')
    width = config.get('thumbnail-width', 50)
    if width:
        width = int(width)
    else:
        width = None
    height = config.get('thumbnail-height', 50)
    if height:
        height = int(height)
    else:
        height = None

    thumbnail_container = zeit.content.image.interfaces.IThumbnailFolder(
        context)
    image_name = context.__name__
    if image_name not in thumbnail_container:
        transform = zeit.content.image.interfaces.ITransform(context)
        method = getattr(transform, method_name)
        thumbnail = method(width, height)

        thumbnail_properties = (
            zeit.connector.interfaces.IWebDAVWriteProperties(thumbnail))
        image_properties = zeit.connector.interfaces.IWebDAVReadProperties(
            context)
        for (name, namespace), value in image_properties.items():
            if namespace != 'DAV:':
                thumbnail_properties[(name, namespace)] = value
        thumbnail_properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)

        thumbnail_container[image_name] = thumbnail

    return thumbnail_container[image_name]


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.content.image.interfaces.IThumbnailFolder)
def thumbnail_folder_factory(context):
    name = u'thumbnails'
    folder = context.__parent__
    if name not in folder:
        folder[name] = zeit.cms.repository.folder.Folder()
    return folder[name]
