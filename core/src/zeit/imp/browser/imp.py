# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.cms.browser.view
import zeit.content.image.interfaces


class Imp(object):

    @property
    def width(self):
        return self.context.getImageSize()[0]

    @property
    def height(self):
        return self.context.getImageSize()[1]


class ImageBar(zeit.cms.browser.view.Base):

    def __call__(self):
        result = []
        for obj in self.context.__parent__.values():
            if not zeit.content.image.interfaces.IImage.providedBy(obj):
                continue
            if obj == self.context:
                continue
            result.append(dict(
                url=self.url(obj),
                name=obj.__name__))
        return cjson.encode(result)
