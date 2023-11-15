from zeit.cms.interfaces import CONFIG_CACHE
from zope.cachedescriptors.property import Lazy as cachedproperty
import collections.abc
import copy
import grokcore.component as grok
import sys
import zeit.cms.content.sources
import zeit.content.image.interfaces
import zeit.edit.body
import zope.schema


@grok.implementer(zeit.content.image.interfaces.IVariants)
class Variants(grok.Adapter, collections.abc.Mapping):
    grok.context(zeit.content.image.interfaces.IImageGroup)

    def __init__(self, context):
        super().__init__(context)
        self.settings = self.context.variants
        self.__parent__ = context

    def __getitem__(self, key):
        """Retrieve Variant for JSON Requests"""
        if key in self.settings:
            variant = Variant(id=key, **self.settings[key])
            config = VARIANT_SOURCE.factory.find(self.context, key)
            self._copy_missing_fields(config, variant)
        else:
            variant = VARIANT_SOURCE.factory.find(self.context, key)

        if not variant.is_default:
            self._copy_missing_fields(self.default_variant, variant)

        variant.__parent__ = self
        return variant

    def _copy_missing_fields(self, source, target):
        """Copy all values from schema fields from source to target if missing.

        Since only schema fields are copied, zope.interface.Attribute fields
        are ignored.

        All schema fields must be initialized with a default value, otherwise
        copying from `source` will fail. Be aware that only `None` is allowed
        as the default value for attributes, since other values are considered
        as `target already has a custom value, so do not inherit from source`.
        To use a default value other than `None`, the default must be defined
        inside the XML config.

        For example: If we set a default of `zoom = 1.0` on `Variant`, this
        would apply to new instances of `source` and `target`. But when setting
        `source.zoom = 0.5` the value will not be copied to `target`, since
        `target` already has a "custom" zoom value of 1.0.

        """
        for key in zope.schema.getFieldNames(zeit.content.image.interfaces.IVariant):
            if hasattr(target, key) and getattr(target, key) is not None:
                continue
            if hasattr(source, key):
                setattr(target, key, getattr(source, key))

    def keys(self):
        return [x.id for x in VARIANT_SOURCE(self.context)]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())

    @cachedproperty
    def default_variant(self):
        if Variant.DEFAULT_NAME in self.settings:
            default = self[Variant.DEFAULT_NAME]
        else:
            default = VARIANT_SOURCE.factory.find(self.context, Variant.DEFAULT_NAME)
        return default


@grok.implementer(zeit.content.image.interfaces.IVariant)
class Variant(zeit.cms.content.sources.AllowedBase):
    DEFAULT_NAME = 'default'
    interface = zeit.content.image.interfaces.IVariant

    aspect_ratio = None
    brightness = None
    contrast = None
    fallback_size = None
    max_size = None
    saturation = None
    sharpness = None

    def __init__(self, **kw):
        super().__init__(kw['id'], kw['id'], kw.get('available'))
        """Set attributes that are part of the Schema and convert their type"""
        fields = zope.schema.getFields(self.interface)
        for key, value in kw.items():
            if key not in fields:
                continue  # ignore attributes that aren't part of the schema
            value = fields[key].fromUnicode(str(value))
            setattr(self, key, value)

    def __eq__(self, other):
        if zeit.content.image.interfaces.IVariant.providedBy(other) and (self.id == other.id):
            return True
        else:
            return False

    def __cmp__(self, other):
        return super().__cmp__(other)

    @property
    def ratio(self):
        """Calculate ratio from aspect ratio or use dimension of master image.

        Normally the aspect_ratio is given as '3:4', resulting in a ratio of
        0.75. However, when aspect_ratio is set to 'original', the ratio will
        be calculated from the dimensions of the source image by ITransform.

        """
        if self.is_default or self.aspect_ratio in [None, 'original']:
            return None
        xratio, yratio = self.aspect_ratio.split(':')
        return float(xratio) / float(yratio)

    @property
    def max_width(self):
        if self.max_size is None:
            return sys.maxsize
        width, height = self.max_size.split('x')
        return int(width)

    @property
    def max_height(self):
        if self.max_size is None:
            return sys.maxsize
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
            return '%s/%s' % (zeit.content.image.imagegroup.Thumbnails.NAME, self.name)
        return '{}/{}__{}'.format(
            zeit.content.image.imagegroup.Thumbnails.NAME, self.name, self.max_size
        )


class VariantSource(
    zeit.cms.content.sources.ObjectSource, zeit.cms.content.sources.SimpleContextualXMLSource
):
    product_configuration = 'zeit.content.image'
    config_url = 'variant-source'
    default_filename = 'image-variants.xml'

    def find(self, context, id):
        result = super().find(context, id)
        if result is None:
            return None
        # Don't let Variants._copy_missing_fields() change cached instances.
        # This is done here so zeit.web can easily circumvent it (since it has
        # to subclass VariantSource anyway) -- as it turns out, creating as
        # many new objects as currently necessitated e.g. by
        # VariantTraverser.all_variants_with_name() is rather expensive.
        return copy.copy(result)

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            sizes = list(node.iterchildren('size'))
            if not sizes:
                # If there are no children, create a Variant from parent node
                attributes = dict(node.attrib)
                attributes['id'] = attributes['name']
                variant = Variant(**attributes)
                result[variant.id] = variant

            for size in sizes:
                # Create Variant for each given size
                variant = Variant(**self._merge_attributes(node.attrib, size.attrib))
                result[variant.id] = variant
        return result

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
            result['id'] = '{}-{}'.format(parent_attr['name'], child_attr['id'])

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
