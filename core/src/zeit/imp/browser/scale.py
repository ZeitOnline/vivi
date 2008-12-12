# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import calendar
import zope.datetime
import zope.dublincore.interfaces
import zeit.cms.browser.view
import zeit.content.image.browser.image
import zeit.imp.mask


class ScaledImage(zeit.content.image.browser.image.Scaled):

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

    def __call__(self, image_width, image_height, mask_width, mask_height):
        image = zeit.imp.mask.Mask(
            (image_width, image_height), (mask_width, mask_height))
        self.request.response.setHeader(
            'Cache-Control', 'public,max-age=86400')
        self.request.response.setHeader('Content-Type', 'image/png')
        return image.open().read()
