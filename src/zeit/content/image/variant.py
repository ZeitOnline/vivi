import UserDict
import grokcore.component as grok
import zeit.cms.content.sources
import zeit.content.image.interfaces
import zeit.edit.body
import zope.schema


class Variants(grok.Adapter, UserDict.DictMixin):

    grok.context(zeit.content.image.interfaces.IImageGroup)
    grok.implements(zeit.content.image.interfaces.IVariants)

    def __init__(self, context):
        super(Variants, self).__init__(context)
        self.__parent__ = context

    def __getitem__(self, key):
        if key in self.context.variants:
            variant = Variant(id=key, **self.context.variants[key])
            config = VARIANT_SOURCE.factory.find(self.context, key)
            self._copy_missing_fields(config, variant)
        else:
            variant = VARIANT_SOURCE.factory.find(self.context, key)
            self._copy_missing_fields(self.default_variant, variant)
        variant.__parent__ = self
        return variant

    def _copy_missing_fields(self, source, target):
        for key in zope.schema.getFieldNames(
                zeit.content.image.interfaces.IVariant):
            if hasattr(target, key):
                continue
            if hasattr(source, key):
                setattr(target, key, getattr(source, key))

    def keys(self):
        keys = [x.id for x in VARIANT_SOURCE(self.context)]
        for key in self.context.variants.keys():
            if key not in keys:
                keys.append(key)
        return keys

    @property
    def default_variant(self):
        if Variant.DEFAULT_NAME in self.context.variants:
            default = self[Variant.DEFAULT_NAME]
        else:
            default = VARIANT_SOURCE.factory.find(
                self.context, Variant.DEFAULT_NAME)
            # XXX Is this really the right place to set default values?
            default.focus_x = 0.5
            default.focus_y = 0.5
            default.zoom = 1
        return default


class Variant(object):

    grok.implements(zeit.content.image.interfaces.IVariant)

    DEFAULT_NAME = 'default'

    def __init__(self, **kw):
        self.__dict__.update(kw)
        if kw.get('ratio'):
            self.ratio_str = self.ratio
            self.xratio, self.yratio = self.ratio.split(':')
            self.ratio = float(self.xratio) / float(self.yratio)

    @property
    def is_default(self):
        return self.id == self.DEFAULT_NAME


class VariantSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.image'
    config_url = 'variant-source'

    def getTitle(self, context, value):
        return value.id

    def getToken(self, context, value):
        return value.id

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for node in tree.getchildren():
            if not self.isAvailable(node, context):
                continue

            attributes = dict(node.attrib)
            if 'name' in attributes:
                attributes['id'] = attributes['name']
                del attributes['name']

            if node.countchildren() == 0:
                result.append(Variant(**attributes))

            for size in node.getchildren():
                size_attr = attributes.copy()
                size_attr.update(size.attrib)
                if 'name' in size_attr:
                    size_attr['id'] = '{}-{}'.format(
                        size_attr['id'], size_attr['name'])
                    del size_attr['name']
                result.append(Variant(**size_attr))
        return result

    def find(self, context, id):
        for value in self.getValues(context):
            if value.id == id:
                return value
        raise KeyError(id)

VARIANT_SOURCE = VariantSource()


class VariantsTraverser(zeit.edit.body.Traverser):

    grok.context(zeit.content.image.interfaces.IImageGroup)
    body_name = 'variants'
    body_interface = zeit.content.image.interfaces.IVariants


@grok.adapter(zeit.content.image.interfaces.IVariants)
@grok.implementer(zeit.content.image.interfaces.IImageGroup)
def imagegroup_for_variants(context):
    return zeit.content.image.interfaces.IImageGroup(context.__parent__)


@grok.adapter(zeit.content.image.interfaces.IVariant)
@grok.implementer(zeit.content.image.interfaces.IImageGroup)
def imagegroup_for_variant(context):
    return zeit.content.image.interfaces.IImageGroup(context.__parent__)
