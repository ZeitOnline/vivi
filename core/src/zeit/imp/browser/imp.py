# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zeit.imp.source
import zope.cachedescriptors.property


class Imp(object):

    @property
    def width(self):
        return self.master_image.getImageSize()[0]

    @property
    def height(self):
        return self.master_image.getImageSize()[1]

    @zope.cachedescriptors.property.Lazy
    def master_image(self):
        return zeit.content.image.interfaces.IMasterImage(self.context)

    def scales(self):
        return zeit.imp.source.ScaleSource()


class ImageBar(zeit.cms.browser.view.Base):

    def __call__(self):
        result = []
        for obj in self.context.values():
            if not zeit.content.image.interfaces.IImage.providedBy(obj):
                continue
            if zeit.content.image.interfaces.IMasterImage.providedBy(obj):
                continue
            scale_name = obj.__name__.replace(
                self.context.__name__ + '-', '', 1)
            scale_name = scale_name.rsplit('.', 1)[0]
            result.append(dict(
                url=self.url(obj),
                name=obj.__name__,
                scale_name=scale_name))
        return cjson.encode(result)
