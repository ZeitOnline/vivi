# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Create cropping mask as PNG with alpha."""

import PIL.Image
import PIL.ImageDraw
import cStringIO


class Mask(object):
    """A mask for cropping.

    The constructed image has a semi-transparent "border" and a transparent
    mask where the image can be cropped from.

    The images are quite small so we don't bother putting them in file.

    """

    def __init__(self, image_size, mask_size, border=None):
        self.image_size, self.mask_size = image_size, mask_size
        image = PIL.Image.new('RGBA', image_size, (200, 200, 200, 220))
        draw = PIL.ImageDraw.ImageDraw(image)
        outline = None
        if border is not None:
            outline=tuple(border) + (255, )
        draw.rectangle(self._get_rect_box(),
                       fill=(255, 0, 0, 0), outline=outline)
        del draw
        self._data = cStringIO.StringIO()
        image.save(self._data, format='PNG')

    def _get_rect_box(self):
        iw, ih = self.image_size
        mw, mh = self.mask_size
        mx1, my1 = (iw/2-mw/2, ih/2-mh/2)
        mx2, my2 = (mx1 + mw - 1), (my1 + mh - 1)
        return ((mx1, my1), (mx2, my2))

    def open(self, mode='r'):
        self._data.seek(0)
        return self._data
