# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import zeit.content.gallery.interfaces
import zeit.imp.interfaces
import zope.component
import zope.interface


@zope.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@zope.interface.implementer(zeit.imp.interfaces.ICropper)
def cropper_for_gallery(context):
    return zeit.imp.interfaces.ICropper(context.image)


class GalleryStorer(object):

    zope.component.adapts(zeit.content.gallery.interfaces.IGalleryEntry)
    zope.interface.implements(zeit.imp.interfaces.IStorer)

    def __init__(self, context):
        self.context = context

    def store(self, name, pil_image):
        gallery = self.context.__parent__
        image = zeit.content.image.image.LocalImage()
        pil_image.save(image.open('w'), 'JPEG', optimize=True, quality=80)

        base_name, ext = os.path.splitext(self.context.__name__)
        image_name = '%s-%s.jpg' % (base_name, name)
        i = 1
        while image_name in gallery:
            i += 1
            image_name = '%s-%s-%s.jpg' % (base_name, name, i)

        entry = zeit.content.gallery.gallery.GalleryEntry()
        for field in zope.schema.getFields(
            zeit.content.gallery.interfaces.IGalleryEntry).values():
            if not field.readonly:
                field.set(entry, field.get(self.context))
        entry.image = image
        entry.is_crop_of = self.context.__name__

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
