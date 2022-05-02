from zeit.cms.interfaces import CONFIG_CACHE
import collections
import six
import zeit.cms.content.sources
import zope.interface


class AllowedMixin(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, available, types):
        super(AllowedMixin, self).__init__(id, title, available)
        self.types = types.split(' ') if types else None

    def is_allowed(self, context):
        # Avoid circular import
        from zeit.content.cp.interfaces import ICenterPage
        cp = ICenterPage(context, None)
        if cp is None:
            return True
        return self.is_allowed_iface(cp) and self.is_allowed_type(cp)

    def is_allowed_iface(self, cp):
        return super(AllowedMixin, self).is_allowed(cp)

    def is_allowed_type(self, cp):
        if not self.types:
            return True
        negative_present = False
        match = False
        for typ in self.types:
            if typ.startswith('!'):
                negative_present = True
                typ = typ.replace('!', '', 1)
            if cp.type == typ:
                match = True
        if negative_present:
            return not match
        else:
            return match


class ITeaserBlockLayout(zope.interface.Interface):
    """Layout of a teaser block."""

    id = zope.schema.ASCIILine(title='Id used in xml to identify layout')
    title = zope.schema.TextLine(title='Human readable title.')
    image_pattern = zope.schema.ASCIILine(
        title='A match for the image to use in this layout.')
    areas = zope.schema.Set(
        title='Kinds of areas where this layout is allowed')
    default_in_areas = zope.schema.Set(
        title='Kinds of areas where this layout is the default')
    types = zope.schema.Set(
        title='Types of CP where this layout is allowed')
    is_leader = zope.schema.Bool(
        title='When auto-filling with teasers, require lead_candiate?')

    def is_default(block):
        """True if this layout is the default for the given block's area."""


@zope.interface.implementer(ITeaserBlockLayout)
class BlockLayout(AllowedMixin):

    def __init__(self, id, title, image_pattern=None,
                 areas=None, default=(), available=None,
                 types=None, is_leader=False):
        super(BlockLayout, self).__init__(id, title, available, types)
        self.image_pattern = image_pattern
        self.areas = frozenset(areas)
        self.default_in_areas = default
        self.is_leader = is_leader

    def is_default(self, block):
        area = zeit.content.cp.interfaces.IArea(block)
        return area.kind in self.default_in_areas


class NoBlockLayout:

    def __init__(self, block):
        self.block = block

    def __getattr__(self, name):
        if name not in ITeaserBlockLayout:
            raise AttributeError(name)
        area = zeit.content.cp.interfaces.IArea(self.block, None)
        raise ValueError(
            'Teaser layout "%s" is not configured for area "%s".\n'
            '  (module:%s, area:%s). Is a default layout set for the area?' % (
                self.block.xml.get('module'),
                getattr(area, 'kind', '<unknown>'),
                self.block.__name__,
                getattr(area, '__name__', '<unknown>')))


class RegionConfig(AllowedMixin):

    def __init__(self, id, title, kind, areas, available, types):
        super(RegionConfig, self).__init__(id, title, available, types)
        self.kind = kind
        self.areas = areas


class AreaConfig(AllowedMixin):

    def __init__(self, id, title, kind, available, types):
        super(AreaConfig, self).__init__(id, title, available, types)
        self.kind = kind


class ModuleConfig(AllowedMixin):

    def __init__(self, id, title, available, types):
        super(ModuleConfig, self).__init__(id, title, available, types)


class ObjectSource(zeit.cms.content.sources.ObjectSource):

    def _get_title_for(self, node):
        return six.text_type(node.get('title'))


class TeaserBlockLayoutSource(
        ObjectSource, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'block-layout-source'
    default_filename = 'cp-layouts.xml'
    attribute = 'id'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            g = node.get
            areas = g('areas')
            areas = areas.split()
            id = node.get(self.attribute)
            result[id] = BlockLayout(
                id, self._get_title_for(node),
                g('image_pattern'), areas, g('default', ''),
                g('available', None), g('types', None), g('is_leader', False))
        return result

    def filterValue(self, context, value):
        if context is None:
            return True
        area = zeit.content.cp.interfaces.IArea(context)
        return area.kind in value.areas


TEASERBLOCK_LAYOUTS = TeaserBlockLayoutSource()


def get_layout(id):
    return TEASERBLOCK_LAYOUTS(None).find(id)


class RegionConfigSource(ObjectSource, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'region-config-source'
    default_filename = 'cp-regions.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for i, node in enumerate(tree.iterchildren('*')):
            # Using kind as ID is not unique, since regions of the same kind
            # can contain different areas and might have different titles.
            # Therefore we need to prefix the kind to make it unique.
            id = '%s-%s' % (i, node.get('kind'))
            result[id] = RegionConfig(
                id, self._get_title_for(node),
                node.get('kind'),
                [dict(x.attrib) for x in node.iterchildren('area')],
                node.get('available', None), node.get('types', None),
            )
        return result


REGION_CONFIGS = RegionConfigSource()


class AreaConfigSource(ObjectSource, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'area-config-source'
    default_filename = 'cp-areas.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            id = node.get('kind')
            result[id] = AreaConfig(
                id, self._get_title_for(node),
                node.get('kind'),
                node.get('available', None), node.get('types', None),
            )
        return result


AREA_CONFIGS = AreaConfigSource()


class ModuleConfigSource(ObjectSource, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'module-config-source'
    default_filename = 'cp-modules.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            id = node.get('id')
            result[id] = ModuleConfig(
                id, self._get_title_for(node),
                node.get('available', None), node.get('types', None),
            )
        return result


MODULE_CONFIGS = ModuleConfigSource()
