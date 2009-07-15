# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import transaction
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zeit.imp.browser.interfaces
import zeit.imp.source
import zope.app.pagetemplate
import zope.cachedescriptors.property


class NoMasterImageErrorView(object):

    def __call__(self):
        transaction.doom()
        return super(NoMasterImageErrorView, self).__call__()


class ImpBase(object):

    template = zope.app.pagetemplate.ViewPageTemplateFile('imp.pt')

    @property
    def width(self):
        return self.image.getImageSize()[0]

    @property
    def height(self):
        return self.image.getImageSize()[1]

    def scales(self):
        return zeit.imp.source.ScaleSource()

    def colors(self):
        return zeit.imp.source.ColorSource()


class Imp(ImpBase):
    """Imp for an ImageFolder."""

    @zope.cachedescriptors.property.Lazy
    def image(self):
        try:
            return zeit.content.image.interfaces.IMasterImage(self.context)
        except TypeError:
            raise zeit.imp.browser.interfaces.NoMasterImageError()


class ImageBar(zeit.cms.browser.view.Base):

    def __call__(self):
        result = []
        for image in self.images:
            scale_name = image.__name__.replace(
                self.context.__name__ + '-', '', 1)
            scale_name = scale_name.rsplit('.', 1)[0]
            result.append(dict(
                url=self.url(image),
                name=image.__name__,
                scale_name=scale_name))
        return cjson.encode(result)

    @property
    def images(self):
        for obj in self.context.values():
            if not zeit.content.image.interfaces.IImage.providedBy(obj):
                continue
            if zeit.content.image.interfaces.IMasterImage.providedBy(obj):
                continue
            yield obj
