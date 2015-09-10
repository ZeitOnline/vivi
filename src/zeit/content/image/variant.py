import UserDict
import collections
import copy
import grokcore.component as grok
import sys
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
        """Retrieve Variant for JSON Requests"""
        if key in self.context.variants:
            variant = Variant(id=key, **self.context.variants[key])
            config = VARIANT_SOURCE.factory.find(self.context, key)
            self._copy_missing_fields(config, variant)
        else:
            variant = VARIANT_SOURCE.factory.find(self.context, key)

        if not variant.is_default:
            self._copy_missing_fields(self.default_variant, variant)

        variant.__parent__ = self
        return variant

    def _copy_missing_fields(self, source, target):
        for key in zope.schema.getFieldNames(
                zeit.content.image.interfaces.IVariant):
            if hasattr(target, key) and getattr(target, key) is not None:
                continue
            if hasattr(source, key):
                setattr(target, key, getattr(source, key))

    def keys(self):
        return [x.id for x in VARIANT_SOURCE(self.context)]

    @property
    def default_variant(self):
        if Variant.DEFAULT_NAME in self.context.variants:
            default = self[Variant.DEFAULT_NAME]
        else:
            default = VARIANT_SOURCE.factory.find(
                self.context, Variant.DEFAULT_NAME)
        return default


class Variant(object):

    DEFAULT_NAME = 'default'
    interface = zeit.content.image.interfaces.IVariant

    grok.implements(interface)

    max_size = None
    brightness = None
    fallback_size = None
    legacy_name = None
    aspect_ratio = None

    def __init__(self, **kw):
        """Set attributes that are part of the Schema and convert their type"""
        fields = zope.schema.getFields(self.interface)
        for key, value in kw.items():
            if key not in fields:
                continue  # ignore attributes that aren't part of the schema
            value = fields[key].fromUnicode(unicode(value))
            setattr(self, key, value)

    def __cmp__(self, other):
        if zeit.content.image.interfaces.IVariant.providedBy(other) and (
                self.id == other.id):
            return 0
        return super(Variant, self).__cmp__(other)

    @property
    def ratio(self):
        if self.is_default or self.aspect_ratio == 'original':
            image = zeit.content.image.interfaces.IMasterImage(
                zeit.content.image.interfaces.IImageGroup(self))
            xratio, yratio = image.getImageSize()
            return float(xratio) / float(yratio)

        if self.aspect_ratio is None:
            return None

        xratio, yratio = self.aspect_ratio.split(':')
        return float(xratio) / float(yratio)

    @property
    def max_width(self):
        if self.max_size is None:
            return sys.maxint
        width, height = self.max_size.split('x')
        return int(width)

    @property
    def max_height(self):
        if self.max_size is None:
            return sys.maxint
        width, height = self.max_size.split('x')
        return int(height)

    @property
    def fallback_width(self):
        if self.fallback_size is None:
            return None
        width, height = self.fallback_size.split('x')
        return int(width)

    @property
    def fallback_height(self):
        if self.fallback_size is None:
            return None
        width, height = self.fallback_size.split('x')
        return int(height)

    @property
    def is_default(self):
        return self.id == self.DEFAULT_NAME

    @property
    def relative_image_path(self):
        if self.max_size is None:
            return '%s/%s' % (
                zeit.content.image.imagegroup.Thumbnails.NAME, self.name)
        return '{}/{}__{}'.format(
            zeit.content.image.imagegroup.Thumbnails.NAME,
            self.name, self.max_size)


class VariantSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.image'
    config_url = 'variant-source'

    def getTitle(self, context, value):
        return value.id

    def getToken(self, context, value):
        return value.id

    def getValues(self, context):
        return self.values(context).values()

    def values(self, context):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue

            sizes = list(node.iterchildren('size'))
            if not sizes:
                # If there are no children, create a Variant from parent node
                attributes = dict(node.attrib)
                attributes['id'] = attributes['name']
                variant = Variant(**attributes)
                result[variant.id] = variant

            for size in sizes:
                # Create Variant for each given size
                variant = Variant(**self._merge_attributes(
                    node.attrib, size.attrib))
                result[variant.id] = variant
        return result

    def find(self, context, id):
        return self.values(context)[id]

    def _merge_attributes(self, parent_attr, child_attr):
        """Merge attributes from parent with those from child.

        Attributes from child are more specific and therefore may overwrite
        attributes from parent. Create the child `id` via concatenation, since
        it should be unique among variants and respects the parent / child
        hierarchy.

        """
        result = copy.copy(parent_attr)
        result.update(child_attr)

        if 'name' in parent_attr and 'id' in child_attr:
            result['id'] = '{}-{}'.format(
                parent_attr['name'], child_attr['id'])

        return result

VARIANT_SOURCE = VariantSource()


class VariantsTraverser(zeit.edit.body.Traverser):

    grok.context(zeit.content.image.interfaces.IRepositoryImageGroup)
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


class LegacyVariantSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.image'
    config_url = 'legacy-variant-source'

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for node in tree.iterchildren('*'):
            result.append({'old': node.get('old'), 'new': node.get('new')})
        return result

LEGACY_VARIANT_SOURCE = LegacyVariantSource()
