import json
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zope.security.proxy


class VariantList(zeit.cms.browser.view.Base):

    def __call__(self):
        return json.dumps([
            serialize_variant(x, self.url) for x in self.context.values()])


class VariantDetail(zeit.cms.browser.view.Base):

    def __call__(self):
        return getattr(self, self.request.method.lower())()

    def get(self):
        return json.dumps(serialize_variant(self.context, self.url))


def serialize_variant(variant, make_url):
    data = zope.security.proxy.getObject(variant).__dict__.copy()
    data.pop('__parent__')
    data['url'] = make_url(zeit.content.image.interfaces.IMasterImage(
        zeit.content.image.interfaces.IImageGroup(variant)), 'raw')
    return data
