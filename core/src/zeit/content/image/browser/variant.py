import json
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zeit.imp.browser.interfaces
import zope.cachedescriptors.property


class Variant(zeit.cms.browser.view.Base):

    @zope.cachedescriptors.property.Lazy
    def image(self):
        try:
            return zeit.content.image.interfaces.IMasterImage(self.context)
        except TypeError:
            raise zeit.imp.browser.interfaces.NoMasterImageError()


class VariantList(Variant):

    def __call__(self):
        return json.dumps([
            {'id': 'zon-foo', 'url': self.url(self.image, 'raw')},
            {'id': 'zon-bar', 'url': self.url(self.image, 'raw'), 'width': '50%'},
            {'id': 'zon-baz', 'url': self.url(self.image, 'raw')},
            {'id': 'zon-1', 'url': self.url(self.image, 'raw'), 'width': '25%'},
            {'id': 'zon-2', 'url': self.url(self.image, 'raw')},
            {'id': 'zon-3', 'url': self.url(self.image, 'raw'), 'width': '75%'},
            {'id': 'zon-4', 'url': self.url(self.image, 'raw')},
        ])
