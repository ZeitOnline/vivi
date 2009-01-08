# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image
import calendar
import zope.datetime
import zope.dublincore.interfaces
import zeit.cms.browser.view
import zeit.content.image.browser.image
import zeit.content.image.interfaces
import zeit.imp.mask


class ScaledImage(zeit.content.image.browser.image.Scaled):

    filter = PIL.Image.NEAREST

    @property
    def width(self):
        return int(float(self.request.get('width', 0)))

    @property
    def height(self):
        return int(float(self.request.get('height', 0)))

    def __call__(self):
        self.request.response.setHeader(
            'Cache-Control', 'public,max-age=3600')
        dc = zope.dublincore.interfaces.IDCTimes(self.scaled.context, None)
        if dc is not None:
            lmd = zope.datetime.rfc1123_date(
                calendar.timegm(dc.modified.utctimetuple()))
            self.request.response.setHeader("Last-Modified", lmd)
        return self.scaled()


class MaskImage(zeit.cms.browser.view.Base):

    def __call__(self, image_width, image_height, mask_width, mask_height,
                 border):
        image = zeit.imp.mask.Mask(
            (image_width, image_height), (mask_width, mask_height), border)
        self.request.response.setHeader(
            'Cache-Control', 'public,max-age=86400')
        self.request.response.setHeader('Content-Type', 'image/png')
        return image.open().read()


class CropImage(zeit.cms.browser.view.Base):

    def __call__(self, w, h, x1, y1, x2, y2, name):
        w, h = int(w), int(h)
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        transform = zeit.content.image.interfaces.ITransform(self.context)
        image = transform.resize(w, h)
        pil_image = PIL.Image.open(image.open())
        format = pil_image.format
        pil_image = pil_image.crop((x1, y1, x2, y2))
        pil_image.save(image.open('w'), 'JPEG')
        image_name = '%s-%s.jpg' % (self.context.__parent__.__name__, name)
        self.context.__parent__[image_name] = image
        return self.url(image)
