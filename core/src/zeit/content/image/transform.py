import PIL.Image
import PIL.ImageColor
import PIL.ImageEnhance
import zope.component
import zope.interface
import zope.security.proxy

import zeit.cms.config
import zeit.cms.repository.folder
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.content.image.interfaces


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.content.image.interfaces.ITransform)
class ImageTransform:
    MAXIMUM_IMAGE_SIZE = 5000

    def __init__(self, context):
        self.context = context
        try:
            with zope.security.proxy.removeSecurityProxy(context.open()) as f:
                self.image = PIL.Image.open(f)
                self.image.load()
        except IOError:
            raise zeit.content.image.interfaces.ImageProcessingError(
                'Cannot transform image %s' % context.__name__
            )

    def thumbnail(self, width, height):
        self.create_thumbnail(self.image, width, height)
        return self._construct_image(self.image)

    @staticmethod
    def create_thumbnail(image: PIL.Image, width, height):
        """Resize PIL.Image in-place, so that it is no larger than the given
        width+height, while preserving the original aspect ratio."""
        orig_width, orig_height = image.size
        orig_ratio = orig_width / orig_height
        target_ratio = width / height
        if target_ratio >= orig_ratio:
            width = height * orig_ratio
        else:
            height = width / orig_ratio

        im = image.resize((int(width), int(height)), PIL.Image.Resampling.LANCZOS)
        # Taken from Image.thumbnail(), to modify in-place.
        image.im = im.im
        image._size = im.size
        image._mode = im.mode
        image.readonly = 0

    def create_variant_image(self, variant, size=None, fill_color=None, format=None):
        """Create variant image from source image.

        Will crop the image according to the zoom, focus point and size. In
        addition, the image is scaled down to size (if given) and image
        enhancements, like brightness, are applied.

        The default variant skips cropping, but still applies image
        enhancements, so it can be used as a high quality preview of image
        enhancements in the frontend.
        """

        if not variant.is_default:
            image = self._crop_variant_image(variant, size=size)
        else:
            # Alpha channel is usually activated when cropping,
            # so we must do it by hand since we skipped cropping
            image = self._enable_alpha_channel(self.image)

        # Apply enhancements like brightness
        if variant.brightness is not None:
            image = PIL.ImageEnhance.Brightness(image).enhance(variant.brightness)
        if variant.contrast is not None:
            image = PIL.ImageEnhance.Contrast(image).enhance(variant.contrast)
        if variant.saturation is not None:
            image = PIL.ImageEnhance.Color(image).enhance(variant.saturation)
        if variant.sharpness is not None:
            image = PIL.ImageEnhance.Sharpness(image).enhance(variant.sharpness)

        # Optionally fill the background of transparent images
        if fill_color not in [None, 'None'] and self._color_mode == 'RGBA':
            fill_color = PIL.ImageColor.getrgb('#' + fill_color)
            opaque = PIL.Image.new('RGB', image.size, fill_color)
            opaque.paste(image, (0, 0), image)
            image = opaque

        return self._construct_image(image, format)

    def _crop_variant_image(self, variant, size=None):
        """Crop variant image from source image.

        Determines crop position using zoom, focus point and size constraint.

        The result image will have the exact dimensions that are predefined by
        the size argument, if provided. Otherwise it depends on the variant
        ratio and zoom only, giving back the best image quality, i.e. will not
        scale down.

        """
        source_width, source_height = self.image.size
        if source_width == 0 or source_height == 0:
            return self.image
        zoomed_width = source_width
        zoomed_height = source_height
        if variant.zoom > 0:
            zoomed_width = int(source_width * variant.zoom)
            zoomed_height = int(source_height * variant.zoom)

        target_ratio = variant.ratio
        if target_ratio is None:
            sw = source_width
            sh = source_height
            target_ratio = (float(sw) / float(sh)) if sh != 0 else 0
        target_width, target_height = self._fit_ratio_to_image(
            zoomed_width, zoomed_height, target_ratio
        )
        if size:
            w, h = size
            if w > 0 and h > 0:
                override_ratio = float(w) / float(h)
                target_width, target_height = self._fit_ratio_to_image(
                    target_width, target_height, override_ratio
                )

        x, y = self._determine_crop_position(variant, target_width, target_height)
        image = self._crop(self.image, x, y, x + target_width, y + target_height)

        if size:
            w, h = size
            if w == 0 or h == 0:
                w, h = self._fit_size_to_ratio(target_width, target_height, w, h, target_ratio)
            if w > self.MAXIMUM_IMAGE_SIZE:
                w = self.MAXIMUM_IMAGE_SIZE
            if h > self.MAXIMUM_IMAGE_SIZE:
                h = self.MAXIMUM_IMAGE_SIZE
            image = image.resize((w, h), PIL.Image.Resampling.LANCZOS)

        return image

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

    def _fit_size_to_ratio(
        self, source_width, source_height, target_width, target_height, target_ratio
    ):
        """Keep the main dimension the same and adjust the other one to fit the
        target ratio. Allow for either dimension to be 0 to fall back on the
        source dimension instead."""
        if not target_width:
            target_width = source_width
        if not target_height:
            target_height = source_height
        if target_ratio >= 1:
            width = min(target_width, source_width)
            height = int(width / target_ratio)
        else:
            height = min(target_height, source_height)
            width = int(height * target_ratio)
        return width, height

    def _determine_crop_position(self, variant, target_width, target_height):
        width, height = self.image.size
        x = int(width * variant.focus_x - target_width * variant.focus_x)
        y = int(height * variant.focus_y - target_height * variant.focus_y)
        return x, y

    def _crop(self, pil_image, x1, y1, x2, y2):
        pil_image = pil_image.crop((x1, y1, x2, y2))
        pil_image = self._enable_alpha_channel(pil_image)
        return pil_image

    @property
    def _color_mode(self):
        # XXX This is a rather crude heuristic.
        return 'RGBA' if self.image.format == 'PNG' else 'RGB'

    def _enable_alpha_channel(self, pil_image):
        """Enable alpha channel for PNG images by converting to RGBA."""
        if pil_image.mode != self._color_mode:
            pil_image = pil_image.convert(self._color_mode)
        return pil_image

    def _construct_image(self, pil_image, format=None):
        image = zeit.content.image.image.TemporaryImage()
        if not format:
            format = self.image.format

        options = zeit.content.image.interfaces.ENCODER_PARAMETERS.find(format)

        with image.open('w') as f:
            pil_image.save(f, format, **options)
        image.__parent__ = self.context
        image_times = zeit.cms.workflow.interfaces.IModified(self.context, None)
        if image_times and image_times.date_last_modified:
            thumb_times = zeit.cms.workflow.interfaces.IModified(image)
            thumb_times.date_last_modified = image_times.date_last_modified
        # Duplicated from z.c.image.image.update_image_properties, to avoid
        # parsing the PIL data *again*.
        (image.width, image.height) = pil_image.size
        image.mimeType = PIL.Image.MIME.get(format, '')
        return image


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.content.image.interfaces.IPersistentThumbnail)
def persistent_thumbnail_factory(context):
    config = zeit.cms.config.package('zeit.content.image')
    width = int(config.get('thumbnail-width', 50))
    height = int(config.get('thumbnail-height', 50))

    container = zeit.content.image.interfaces.IThumbnailFolder(context)
    name = context.__name__
    if name not in container:
        transform = zeit.content.image.interfaces.ITransform(context)
        image = transform.thumbnail(width, height)
        properties = zeit.connector.interfaces.IWebDAVWriteProperties(image)
        properties.pop(zeit.connector.interfaces.UUID_PROPERTY, None)
        container[name] = image

    return container[name]


THUMBNAIL_FOLDER_NAME = 'thumbnails'


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.content.image.interfaces.IThumbnailFolder)
def thumbnail_folder_factory(context):
    folder = context.__parent__
    if THUMBNAIL_FOLDER_NAME not in folder:
        folder[THUMBNAIL_FOLDER_NAME] = zeit.cms.repository.folder.Folder()
    return folder[THUMBNAIL_FOLDER_NAME]
