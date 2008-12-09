# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Create cropping mask as PNG with alpha."""

import PIL.Image
import PIL.ImageDraw
import zeit.content.image.image


class Mask(zeit.content.image.image.LocalImage):

    uniqueId = None

    def __init__(self, image_size, mask_size):
        self.image_size, self.mask_size = image_size, mask_size
        image = PIL.Image.new('RGBA', image_size, (200, 200, 200, 128))
        draw = PIL.ImageDraw.ImageDraw(image)
        draw.rectangle(self._get_rect_box(), fill=(255,0,0, 0))
        del draw
        fh = self.open('w')
        image.save(fh, format='PNG')
        fh.close()

    def _get_rect_box(self):
        iw, ih = self.image_size
        mw, mh = self.mask_size
        return ((iw/2-mw/2, ih/2-mh/2),(iw/2+mw/2, ih/2+mh/2))
