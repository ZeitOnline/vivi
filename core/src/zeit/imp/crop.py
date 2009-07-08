# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image
import PIL.ImageColor
import PIL.ImageEnhance
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.imp.interfaces
import zope.component
import zope.interface
import zope.security.proxy


class Cropper(object):

    zope.component.adapts(zeit.content.image.interfaces.IImage)
    zope.interface.implements(zeit.imp.interfaces.ICropper)

    filter_map = {
        'color': PIL.ImageEnhance.Color,
        'brightness': PIL.ImageEnhance.Brightness,
        'contrast': PIL.ImageEnhance.Contrast,
        'sharpness': PIL.ImageEnhance.Sharpness,
    }

    pil_image = None
    downsample_filter = PIL.Image.ANTIALIAS

    def __init__(self, context):
        self.context = self.__parent__ = context
        self.filters = []

    def add_filter(self, name, factor):
        filter_class = self.filter_map.get(name)
        if filter_class is None:
            raise ValueError(name)
        self.filters.append((filter_class, factor))

    def crop(self, w, h, x1, y1, x2, y2, border=None):
        pil_image = PIL.Image.open(
            zope.security.proxy.removeSecurityProxy(self.context).open())

        pil_image = pil_image.resize((w, h), self.downsample_filter)
        pil_image = pil_image.crop((x1, y1, x2, y2))

        for filter_class, factor in self.filters:
            filter = filter_class(pil_image)
            pil_image = filter.enhance(factor)

        if border is not None:
            pil_image = self.add_border(pil_image, border)

        self.pil_image = pil_image
        return pil_image

    def add_border(self, pil_image, border):
        draw = PIL.ImageDraw.ImageDraw(pil_image)
        w, h = pil_image.size
        if PIL.Image.getmodebase(pil_image.mode) == 'L':
            r, g, b = border
            border = r*299/1000 + g*587/1000 + b*114/1000
        else:
            border = tuple(border) + (255,)
        draw.rectangle((0, 0, w-1, h-1),
                       outline=border)
        return pil_image


@zope.component.adapter(zeit.content.image.interfaces.IRepositoryImageGroup)
@zope.interface.implementer(zeit.imp.interfaces.ICropper)
def cropper_for_imagegroup(context):
    image = zeit.content.image.interfaces.IMasterImage(context)
    return zeit.imp.interfaces.ICropper(image)


@zope.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@zope.interface.implementer(zeit.imp.interfaces.ICropper)
def cropper_for_gallery(context):
    return zeit.imp.interfaces.ICropper(context.image)


class ImageGroupStorer(object):

    zope.component.adapts(zeit.content.image.interfaces.IRepositoryImageGroup)
    zope.interface.implements(zeit.imp.interfaces.IStorer)

    def __init__(self, context):
        self.context = self.__parent__ = context

    def store(self, name, pil_image):
        image = zeit.content.image.image.LocalImage()
        pil_image.save(image.open('w'), 'JPEG', optimize=True, quality=80)
        image_name = '%s-%s.jpg' % (self.context.__name__, name)
        self.context[image_name] = image
        return image


class GalleryStorer(object):

    zope.component.adapts(zeit.content.gallery.interfaces.IGalleryEntry)
    zope.interface.implements(zeit.imp.interfaces.IStorer)

    def __init__(self, context):
        self.context = context

    def store(self, name, pil_image):
        image = zeit.content.image.image.LocalImage()
        pil_image.save(image.open('w'), 'JPEG', optimize=True, quality=80)
        image_name = '%s-%s.jpg' % (self.context.__name__, name)
        entry = zeit.content.gallery.gallery.GalleryEntry()
        for field in zope.schema.getFields(
            zeit.content.gallery.interfaces.IGalleryEntry).values():
            field.set(entry, field.get(self.context))
        entry.image = image

        self.context.__parent__.image_folder[image_name] = image
        self.context.__parent__[image_name] = entry
        self.context.__parent__.reload_image_folder()
        return self.context.__parent__[image_name]
