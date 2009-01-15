# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image
import zeit.content.image.interfaces
import zeit.imp.interfaces
import zope.component
import zope.interface


class Cropper(object):

    zope.component.adapts(zeit.content.image.interfaces.IRepositoryImageGroup)
    zope.interface.implements(zeit.imp.interfaces.ICropper)

    def __init__(self, context):
        self.context = context

    def crop(self, w, h, x1, y1, x2, y2, name, border=False):
        pil_image = PIL.Image.open(self.master_image.open())

        pil_image = pil_image.resize((w, h), PIL.Image.ANTIALIAS)
        pil_image = pil_image.crop((x1, y1, x2, y2))
        if border:
            pil_image = self.add_border(pil_image)

        image = zeit.content.image.image.LocalImage()
        pil_image.save(image.open('w'), 'JPEG')

        image_name = '%s-%s.jpg' % (self.context.__name__, name)
        self.context[image_name] = image
        return image

    def add_border(self, pil_image):
        draw = PIL.ImageDraw.ImageDraw(pil_image)
        w, h = pil_image.size
        draw.rectangle((0, 0, w-1, h-1),
                       outline=(0, 0, 0, 255))
        return pil_image

    @property
    def master_image(self):
        return zeit.content.image.interfaces.IMasterImage(self.context)
