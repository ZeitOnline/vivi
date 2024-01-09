from io import BytesIO

import PIL.Image
import PIL.ImageDraw


class Mask:
    """A mask for cropping (PNG with alpha channel).

    The constructed image has a semi-transparent "border" and a transparent
    mask where the image can be cropped from.

    The images are quite small so we don't bother putting them in file.

    """

    def __init__(
        self, image_size, mask_size, border=None, cross_size=6, cross_color=(0, 255, 0, 128)
    ):
        self.image_size, self.mask_size = image_size, mask_size
        image = PIL.Image.new('RGBA', image_size, (200, 200, 200, 220))
        draw = PIL.ImageDraw.ImageDraw(image)
        outline = None
        if border is not None:
            outline = tuple(border) + (255,)
        visible = self._get_rect_box()
        draw.rectangle(visible, fill=(255, 0, 0, 0), outline=outline)

        mw, mh = self.mask_size
        cx = mw / 2 + visible[0][0]
        cy = mh / 2 + visible[0][1]
        draw.line([(cx - cross_size, cy), (cx + cross_size, cy)], fill=cross_color, width=1)
        draw.line([(cx, cy - cross_size), (cx, cy + cross_size)], fill=cross_color, width=1)

        del draw
        self._data = BytesIO()
        image.save(self._data, format='PNG')

    def _get_rect_box(self):
        iw, ih = self.image_size
        mw, mh = self.mask_size
        mx1, my1 = (iw / 2 - mw / 2, ih / 2 - mh / 2)
        mx2, my2 = (mx1 + mw - 1), (my1 + mh - 1)
        return ((mx1, my1), (mx2, my2))

    def open(self, mode='r'):
        self._data.seek(0)
        return self._data
