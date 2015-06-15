import json
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zope.security.proxy


class VariantSerializeMixin(object):

    def serialize_variant(self, variant):
        base_url = self.url(zeit.content.image.interfaces.IImageGroup(variant))
        data = zope.security.proxy.getObject(variant).__dict__.copy()
        data.pop('__parent__')
        data['url'] = '%s/%s/raw' % (base_url, variant.relative_image_path)
        return data

    def deserialize_variant(self, data):
        result = {}
        for name in ['focus_x', 'focus_y', 'zoom']:
            result[name] = data[name]
        return result


class VariantList(
        zeit.cms.browser.view.Base,
        VariantSerializeMixin):

    def __call__(self):
        return json.dumps(
            [self.serialize_variant(x) for x in self.context.values()
             if not x.is_default])


class VariantDetail(
        zeit.cms.browser.view.Base,
        VariantSerializeMixin):

    def GET(self):
        data = self.serialize_variant(self.context)
        return json.dumps(data)

    def PUT(self):
        body = json.loads(self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH'])))
        group = zeit.content.image.interfaces.IImageGroup(self.context)
        # dicts are not allowed to be changed by security, but since we'll
        # overwrite the dict completely anyway we don't care.
        data = zope.security.proxy.getObject(group.variants)
        data[self.context.id] = self.deserialize_variant(body)
        group.variants = data
