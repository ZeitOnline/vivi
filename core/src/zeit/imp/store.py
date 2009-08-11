# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

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
