import json
import zeit.cms.browser.view
import zeit.content.image.interfaces
import zope.security.proxy


class VariantSerializeMixin:

    def render(self, data=None):
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(data)

    def serialize_variant(self, variant):
        data = {}
        for field in zeit.content.image.interfaces.IVariant:
            data[field] = getattr(variant, field, None)

        base_url = self.url(zeit.content.image.interfaces.IImageGroup(variant))
        image_url = '%s/%s/raw' % (base_url, variant.relative_image_path)
        data['url'] = image_url

        return data

    def deserialize_variant(self, data):
        result = {}
        for name in ['focus_x', 'focus_y', 'zoom']:
            if data[name] is None:
                raise ValueError(
                    "Neither focuspoint nor zoom should ever be set to None, "
                    "since image creation would break.")
            result[name] = data[name]

        # Ignore None values for image enhancements, rather raising an error,
        # since Backbone.js always sends ALL model fields. So setting contrast
        # for the first time will send brightness etc. with a value of `None`,
        # since this is the default value.
        for name in ['brightness', 'contrast', 'saturation', 'sharpness']:
            if data[name] is not None:
                result[name] = data[name]
        return result


class VariantList(
        zeit.cms.browser.view.Base,
        VariantSerializeMixin):

    def __call__(self):
        return self.render(
            [self.serialize_variant(x) for x in self.context.values()
             if not x.is_default])


class VariantDetail(
        zeit.cms.browser.view.Base,
        VariantSerializeMixin):

    def GET(self):
        data = self.serialize_variant(self.context)
        return self.render(data)

    def PUT(self):
        body = json.loads(self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH'])))
        group = zeit.content.image.interfaces.IImageGroup(self.context)
        # dicts are not allowed to be changed by security, but since we'll
        # overwrite the dict completely anyway we don't care.
        data = zope.security.proxy.getObject(group.variants)
        data[self.context.id] = self.deserialize_variant(body)
        group.variants = data
        return self.render()

    def DELETE(self):
        group = zeit.content.image.interfaces.IImageGroup(self.context)
        if self.context.id not in group.variants:
            return b''
        # dicts are not allowed to be changed by security, but since we'll
        # overwrite the dict completely anyway we don't care.
        data = zope.security.proxy.getObject(group.variants)
        del data[self.context.id]
        group.variants = data
        return self.render()


class Editor:

    def __call__(self):
        # Force generating thumbnail source if does not exist yet, so not each
        # variant preview tries to do it simultaneously later on (which only
        # leads to conflicts).
        zeit.content.image.interfaces.IThumbnails(self.context).source_image
        return super().__call__()
