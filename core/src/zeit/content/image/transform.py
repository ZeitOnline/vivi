import PIL.Image
import transaction
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

    def create_variant_image(self, variant, size=None):
        source_width, source_height = self.image.size
        zoomed_width = int(source_width * variant.zoom)
        zoomed_height = int(source_height * variant.zoom)

        target_width, target_height = self._fit_ratio_to_image(
            zoomed_width, zoomed_height, variant.ratio)
        if size is not None:
            w, h = size
            override_ratio = float(w) / float(h)
            target_width, target_height = self._fit_ratio_to_image(
                target_width, target_height, override_ratio)

        x, y = self._determine_crop_position(
            variant, target_width, target_height)
        image = self._crop(
            self.image, x, y, x + target_width, y + target_height)

        if size is not None:
            image = image.resize(size, PIL.Image.ANTIALIAS)

        return self._construct_image(image)

    def _fit_ratio_to_image(self, source_width, source_height, target_ratio):
        """Calculate the biggest (width, height) inside the source that adheres
        to target ratio"""
        original_ratio = float(source_width) / float(source_height)
        if target_ratio > original_ratio:
            width = source_width
            height = int(source_width / target_ratio)
        else:
            width = int(source_height * target_ratio)
            height = source_height
        return width, height

    def _determine_crop_position(self, variant, target_width, target_height):
        width, height = self.image.size
        x = int(width * variant.focus_x - target_width * variant.focus_x)
        y = int(height * variant.focus_y - target_height * variant.focus_y)
        return x, y

    def _crop(self, pil_image, x1, y1, x2, y2):
        pil_image = pil_image.crop((x1, y1, x2, y2))
        # XXX This is a rather crude heuristic.
        mode = 'RGBA' if self.context.format == 'PNG' else 'RGB'
        if pil_image.mode != mode:
            pil_image = pil_image.convert(mode)
        return pil_image

    def _construct_image(self, pil_image):
        image = zeit.content.image.image.LocalImage()
        image.mimeType = self.context.mimeType
        # XXX Maybe encoder setting should be made configurable.
        if self.context.format.upper() in ('JPG', 'JPEG'):
            options = {'progressive': True, 'quality': 85, 'optimize': True}
        elif self.context.format.upper() in ('PNG',):
            options = {'optimize': True}
        else:
            options = {}
        pil_image.save(image.open('w'), self.image.format, **options)
        image.__parent__ = self.context
        image_times = zope.dublincore.interfaces.IDCTimes(self.context)
        if image_times.modified:
            thumb_times = zope.dublincore.interfaces.IDCTimes(image)
            thumb_times.modified = image_times.modified

        def cleanup(commited, image):
            # Releasing the last reference triggers the weakref cleanup of
            # ZODB.blob.Blob, since this local_data Blob never was part of
            # a ZODB connection, which will delete the temporary file.
            image.local_data = None
        transaction.get().addAfterCommitHook(cleanup, [image])

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
