# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.image.image
import zeit.content.image.interfaces
import zeit.imp.interfaces
import zope.component
import zope.interface


class ImageGroupStorer(object):

    zope.component.adapts(zeit.content.image.interfaces.IRepositoryImageGroup)
    zope.interface.implements(zeit.imp.interfaces.IStorer)

    def __init__(self, context):
        self.context = self.__parent__ = context

    def store(self, name, pil_image):
        image = zeit.content.image.image.LocalImage()
        image_format = zeit.content.image.interfaces.IMasterImage(
            self.context).format
        # Luckily, PIL simply ignores kwargs that are not supported by a
        # format, so we can always specify quality, even though it only makes
        # sense for JPEG, but not PNG.
        pil_image.save(
            image.open('w'), image_format, optimize=True, quality=80)
        extension = image_format.lower()
        # XXX Ugly heuristic, but using .jpg is not only generally nicer, but
        # also backwards-compatible behaviour.
        if extension == 'jpeg':
            extension = 'jpg'
        image_name = '%s-%s.%s' % (self.context.__name__, name, extension)
        self.context[image_name] = image

        return image
