# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image
import PIL.ImageDraw
import PIL.ImageColor
import StringIO
import calendar
import zope.datetime
import zope.dublincore.interfaces
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zeit.imp.mask


def parse_filter_args(request, crop):
    for key, value in request.form.items():
        if key.startswith('filter.'):
            filter_type = key.split('.', 1)[1]
            try:
                factor = float(value)
            except ValueError:
                continue
            crop.add_filter(filter_type, factor)


class ScaledImage(zeit.cms.browser.view.Base):

    def __call__(self, width, height):
        width, height = int(width), int(height)
        cropper = zeit.imp.interfaces.ICropper(self.context)
        cropper.downsample_filter = PIL.Image.NEAREST
        parse_filter_args(self.request, cropper)
        pil_image = cropper.crop(width, height, 0, 0, width, height)
        f = StringIO.StringIO()
        pil_image.save(f, 'JPEG')
        self.request.response.setHeader(
            'Cache-Control', 'public,max-age=3600')
        self.request.response.setHeader(
            'Content-Type', 'image/jpeg')
        # Hellooo memory consumption
        return f.getvalue()


class MaskImage(zeit.cms.browser.view.Base):

    def __call__(self, image_width, image_height, mask_width, mask_height,
                 border):
        image = zeit.imp.mask.Mask(
            (int(image_width), int(image_height)),
            (int(mask_width), int(mask_height)),
            parse_border(border))
        self.request.response.setHeader(
            'Cache-Control', 'public,max-age=86400')
        self.request.response.setHeader('Content-Type', 'image/png')
        return image.open().read()


class CropImage(zeit.cms.browser.view.Base):

    def __call__(self, w, h, x1, y1, x2, y2, name, border=''):
        w, h = int(w), int(h)
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cropper = zeit.imp.interfaces.ICropper(self.context)
        parse_filter_args(self.request, cropper)
        cropper.crop(w, h, x1, y1, x2, y2, parse_border(border))
        image = zeit.imp.interfaces.IStorer(self.context).store(name, cropper.pil_image)
        return self.url(image)


def parse_border(border):
    border_color = None
    if border:
        try:
            border_color = PIL.ImageColor.getrgb(border)
        except ValueError:
            pass
    return border_color
