# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.imp.browser.imp
import zeit.content.gallery.interfaces
import zeit.imp.browser.scale
import zope.cachedescriptors.property


class Imp(zeit.imp.browser.imp.ImpBase):

    def render(self):
        if self.context.is_crop_of:
            # XXX this might fail!
            original = self.context.__parent__[self.context.is_crop_of]
            return self.redirect(self.url(original, '@@imp.html'))
        return super(Imp, self).render()

    @zope.cachedescriptors.property.Lazy
    def image(self):
        return self.context.image

    def scales(self):
        return zeit.content.gallery.interfaces.ScaleSource()

    @property
    def previous(self):
        return self.get_image_with_offset(-1)

    @property
    def next(self):
        return self.get_image_with_offset(1)

    @zope.cachedescriptors.property.Lazy
    def original_entries(self):
        gallery = self.context.__parent__
        return [entry for entry in gallery.values()
                if entry.is_crop_of is None]

    def get_image_with_offset(self, offset):
        index = [e.__name__ for e in self.original_entries].index(
            self.context.__name__)
        new_index = index + offset
        if new_index >= 0:
            try:
                return self.original_entries[new_index]
            except KeyError:
                pass


class ImageBar(zeit.imp.browser.imp.ImageBar):

    @property
    def images(self):
        return self.context.crops


class ScaledImage(zeit.imp.browser.scale.ScaledImage):

    def __call__(self, width, height):
        return self.get_scaled_image(self.context.image, width, height)
