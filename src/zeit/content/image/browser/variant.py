import json
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zope.security.proxy


class VariantList(zeit.cms.browser.view.Base):

    def __call__(self):
        return json.dumps([
            serialize_variant(x, self.url, 'random')
            for x in self.context.values()])


class VariantDetail(zeit.cms.browser.view.Base):

    def GET(self):
        return json.dumps(serialize_variant(
            self.context, self.url, 'raw'))

    def PUT(self):
        body = json.loads(self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH'])))
        group = zeit.content.image.interfaces.IImageGroup(self.context)
        # dicts are not allowed to be changed by security, but since we'll
        # overwrite the dict completely anyway we don't care.
        data = zope.security.proxy.getObject(group.variants)
        data[self.context.id] = deserialize_variant(body)
        group.variants = data


def serialize_variant(variant, make_url, view_name):
    data = zope.security.proxy.getObject(variant).__dict__.copy()
    data.pop('__parent__')
    data['url'] = make_url(zeit.content.image.interfaces.IMasterImage(
        zeit.content.image.interfaces.IImageGroup(variant)), view_name)
    return data


def deserialize_variant(data):
    result = {}
    for name in ['focus_x', 'focus_y']:
        result[name] = data[name]
    return result
