from zeit.content.image.imagegroup import Thumbnails
import json
import transaction
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zeit.imp.browser.interfaces
import zeit.imp.source
import zope.app.pagetemplate
import zope.cachedescriptors.property


class NoMasterImageErrorView:

    def __call__(self):
        transaction.doom()
        return super().__call__()


class ImpBase(zeit.cms.browser.view.Base):

    template = zope.app.pagetemplate.ViewPageTemplateFile('imp.pt')

    @property
    def width(self):
        return self.image.getImageSize()[0]

    @property
    def height(self):
        return self.image.getImageSize()[1]

    def scales(self):
        return zeit.imp.source.ScaleSource()(self.context)

    def colors(self):
        return zeit.imp.source.ColorSource()(self.context)


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
        return json.dumps(result)

    @property
    def images(self):
        for obj in self.context.values():
            if not zeit.content.image.interfaces.IImage.providedBy(obj):
                continue
            if zeit.content.image.interfaces.IMasterImage.providedBy(obj):
                continue
            if obj.__name__.startswith(Thumbnails.SOURCE_IMAGE_PREFIX):
                continue
            yield obj
