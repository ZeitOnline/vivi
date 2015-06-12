import json
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zope.security.proxy


class VariantList(zeit.cms.browser.view.Base):

    def __call__(self):
        base_url = self.url(zeit.content.image.interfaces.IImageGroup(
            self.context))
        return json.dumps(
            [serialize_variant(x, base_url) for x in self.context.values()
             if not x.is_default])


class VariantDetail(zeit.cms.browser.view.Base):

    def GET(self):
        base_url = self.url(zeit.content.image.interfaces.IImageGroup(
            self.context))
        data = serialize_variant(self.context, base_url)
        return json.dumps(data)

    def PUT(self):
        body = json.loads(self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH'])))
        group = zeit.content.image.interfaces.IImageGroup(self.context)
        # dicts are not allowed to be changed by security, but since we'll
        # overwrite the dict completely anyway we don't care.
        data = zope.security.proxy.getObject(group.variants)
        data[self.context.id] = deserialize_variant(body)
        group.variants = data


def serialize_variant(variant, base_url):
    data = zope.security.proxy.getObject(variant).__dict__.copy()
    data.pop('__parent__')
    data['url'] = '%s/%s/raw' % (base_url, variant.relative_image_path)
    return data


def deserialize_variant(data):
    result = {}
    for name in ['focus_x', 'focus_y', 'zoom']:
        result[name] = data[name]
    return result
