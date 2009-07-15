# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zeit.imp.browser.imp
import zeit.imp.browser.interfaces
import zeit.imp.browser.scale
import zeit.imp.source
import zope.cachedescriptors.property


class Imp(zeit.imp.browser.imp.ImpBase):

    @zope.cachedescriptors.property.Lazy
    def image(self):
        return self.context.image

    def scales(self):
        return zeit.imp.source.ScaleSource()

    @property
    def previous(self):
        gallery = self.context.__parent__
        images = list(gallery.values())
        current = list(gallery.keys()).index(self.context.__name__)
        for i in range(current - 1, -1, -1):
            image = images[i]
            if not image.is_crop:
                return image

    # XXX duplicate code previous/next
    @property
    def next(self):
        gallery = self.context.__parent__
        images = list(gallery.values())
        current = list(gallery.keys()).index(self.context.__name__)
        for i in range(current + 1, len(gallery)):
            image = images[i]
            if not image.is_crop:
                return image


class ImageBar(zeit.imp.browser.imp.ImageBar):

    @property
    def images(self):
        return self.context.crops


class ScaledImage(zeit.imp.browser.scale.ScaledImage):

    def __call__(self, width, height):
        return self.get_scaled_image(self.context.image, width, height)
