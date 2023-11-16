import os.path
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.crop.interfaces
import zope.component
import zope.interface
import zope.schema.interfaces


@zope.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@zope.interface.implementer(zeit.crop.interfaces.ICropper)
def cropper_for_gallery(context):
    return zeit.crop.interfaces.ICropper(context.image)


@zope.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@zope.interface.implementer(zeit.crop.interfaces.IStorer)
class GalleryStorer:
    def __init__(self, context):
        self.context = context
        self.gallery = self.context.__parent__

    def store(self, name, pil_image):
        image = zeit.content.image.image.LocalImage()
        with image.open('w') as f:
            pil_image.save(f, 'JPEG', optimize=True, quality=80)

        self.copy_image_metadata(image)
        new_entry = self.copy_entry(image)
        new_entry = self.store_image(image, new_entry, name)
        self.hide_related_images(new_entry)
        self.update_order(new_entry)

        return self.gallery[new_entry.__name__]

    def copy_image_metadata(self, image):
        source = zeit.content.image.interfaces.IImageMetadata(self.context.image)
        destination = zeit.content.image.interfaces.IImageMetadata(image)
        for name in zeit.content.image.interfaces.IImageMetadata:
            field = zeit.content.image.interfaces.IImageMetadata[name]
            if not zope.schema.interfaces.IField.providedBy(field):
                continue
            value = getattr(source, name, self)  # use self as marker
            if value is self:
                continue
            setattr(destination, name, value)

    def copy_entry(self, image):
        entry = zeit.content.gallery.gallery.GalleryEntry()
        for field in zope.schema.getFields(zeit.content.gallery.interfaces.IGalleryEntry).values():
            if not field.readonly:
                field.set(entry, field.get(self.context))
        entry.image = image
        entry.is_crop_of = self.context.__name__
        return entry

    def store_image(self, image, entry, name):
        base_name, ext = os.path.splitext(self.context.__name__)
        image_name = '%s-%s.jpg' % (base_name, name)
        self.gallery.image_folder[image_name] = image
        self.gallery[image_name] = entry
        entry = self.gallery[image_name]
        # Delete thumbnail and recreate by getting the entry again
        del entry.thumbnail.__parent__[entry.thumbnail.__name__]
        entry = self.gallery[image_name]
        return entry

    def hide_related_images(self, entry):
        """Hide the original entry and all of its old crops."""
        self.context.layout = 'hidden'
        self.gallery[self.context.__name__] = self.context
        for crop in self.context.crops:
            crop.layout = 'hidden'
            self.gallery[crop.__name__] = crop
        if entry.layout == 'hidden':
            entry.layout = None
        self.gallery[entry.__name__] = entry

    def update_order(self, entry):
        # sort the new entry after its origin
        keys = list(self.gallery.keys())
        origin = keys.index(self.context.__name__)
        keys.remove(entry.__name__)
        keys.insert(origin + 1, entry.__name__)
        self.gallery.updateOrder(keys)
