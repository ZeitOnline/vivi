import zeit.content.gallery.interfaces
import zeit.crop.browser.crop
import zeit.crop.browser.scale
import zope.cachedescriptors.property


class Imp(zeit.crop.browser.crop.ImpBase):
    def render(self):
        if self.context.is_crop_of:
            # XXX this might fail!
            original = self.context.__parent__[self.context.is_crop_of]
            return self.redirect(self.url(original, '@@imp.html'))
        return super().render()

    @zope.cachedescriptors.property.Lazy
    def image(self):
        return self.context.image

    def scales(self):
        return zeit.content.gallery.interfaces.ScaleSource()(self.context)

    @property
    def previous(self):
        return self.get_image_with_offset(-1)

    @property
    def next(self):
        return self.get_image_with_offset(1)

    @zope.cachedescriptors.property.Lazy
    def original_entries(self):
        gallery = self.context.__parent__
        return [entry for entry in gallery.values() if entry.is_crop_of is None]

    def get_image_with_offset(self, offset):
        index = [e.__name__ for e in self.original_entries].index(self.context.__name__)
        new_index = index + offset
        if new_index < 0:
            return None
        try:
            return self.original_entries[new_index]
        except KeyError:
            pass


class ImageBar(zeit.crop.browser.crop.ImageBar):
    @property
    def images(self):
        return self.context.crops


class ScaledImage(zeit.crop.browser.scale.ScaledImage):
    def __call__(self, width, height):
        return self.get_scaled_image(self.context.image, width, height)
