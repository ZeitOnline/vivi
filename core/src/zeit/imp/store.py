# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.gallery.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.imp.interfaces
import zope.component
import zope.interface
import zope.schema


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
            if not field.readonly:
                field.set(entry, field.get(self.context))
        entry.image = image
        entry.is_crop = True

        gallery = self.context.__parent__
        gallery.image_folder[image_name] = image
        gallery[image_name] = entry
        entry = gallery[image_name]

        gallery.reload_image_folder()

        # hide the original entry and all of its crops except for the newly
        # created one
        self.context.hidden = True
        gallery[self.context.__name__] = self.context
        for crop in self.context.crops:
            crop.hidden = True
            # XXX restructure GalleryEntry similar to blocks in a centerpage,
            # so that changes persist directly
            gallery[crop.__name__] = crop
        entry.hidden = False
        gallery[entry.__name__] = entry

        # sort the new entry after its origin
        keys = list(gallery.keys())
        origin = keys.index(self.context.__name__)
        keys.remove(entry.__name__)
        keys.insert(origin + 1, entry.__name__)
        gallery.updateOrder(keys)

        return self.context.__parent__[entry.__name__]
