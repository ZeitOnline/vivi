import UserDict
import grokcore.component as grok
import zeit.cms.content.sources
import zeit.content.image.interfaces
import zeit.edit.body


class Variants(grok.Adapter, UserDict.DictMixin):

    grok.context(zeit.content.image.interfaces.IImageGroup)
    grok.implements(zeit.content.image.interfaces.IVariants)

    def __init__(self, context):
        super(Variants, self).__init__(context)
        self.__parent__ = context

    def __getitem__(self, key):
        if key in self.context.variants:
            variant = Variant(id=key, **self.context.variants[key])
        else:
            variant = VARIANT_SOURCE.factory.find(self.context, key)
        if variant is None:
            raise KeyError(key)
        variant.__parent__ = self
        return variant

    def keys(self):
        keys = [x.id for x in VARIANT_SOURCE(self.context)]
        for key in self.context.variants.keys():
            if key not in keys:
                keys.append(key)
        return keys


class Variant(object):

    grok.implements(zeit.content.image.interfaces.IVariant)

    def __init__(self, **kw):
        self.__dict__.update(kw)


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
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            result.append(Variant(
                id=node.get('name'), ratio=node.get('ratio')))
        return result

    def find(self, context, id):
        for value in self.getValues(context):
            if value.id == id:
                return value
        return None

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
