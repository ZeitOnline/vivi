# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.image.browser.image


class ScaledImage(zeit.content.image.browser.image.Scaled):

    @property
    def width(self):
        return int(float(self.request.get('width', 0)))

    @property
    def height(self):
        return int(float(self.request.get('height', 0)))
