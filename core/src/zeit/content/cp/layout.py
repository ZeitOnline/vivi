from zeit.cms.application import CONFIG_CACHE
import collections
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

    id = zope.schema.ASCIILine(title=u'Id used in xml to identify layout')
    title = zope.schema.TextLine(title=u'Human readable title.')
    image_pattern = zope.schema.ASCIILine(
        title=u'A match for the image to use in this layout.')
    columns = zope.schema.Int(
        title=u'Columns',
        min=1,
        max=2,
        default=1)
    areas = zope.schema.Set(
        title=u'Kinds of areas where this layout is allowed')
    default_in_areas = zope.schema.Bool(
        title=u'Kinds of areas where this layout is the default')
    types = zope.schema.Set(
        title=u'Types of CP where this layout is allowed')

    def is_default(block):
        """True if this layout is the default for the given block's area."""


class BlockLayout(AllowedMixin):

    zope.interface.implements(ITeaserBlockLayout)

    def __init__(self, id, title, image_pattern=None,
                 areas=None, columns=1, default=False, available=None,
                 types=None):
        super(BlockLayout, self).__init__(id, title, available, types)
        self.image_pattern = image_pattern
        self.areas = frozenset(areas)
        self.columns = columns
        self.default_in_areas = default

    def is_default(self, block):
        area = zeit.content.cp.interfaces.IArea(block)
        return area.kind in self.default_in_areas


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
        return unicode(node.get('title'))


class TeaserBlockLayoutSource(
        ObjectSource, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'block-layout-source'
    attribute = 'id'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            g = node.get
            areas = g('areas')
            areas = areas.split()
            columns = g('columns', 1)
            if columns:
                columns = int(columns)
            id = node.get(self.attribute)
            result[id] = BlockLayout(
                id, self._get_title_for(node),
                g('image_pattern'), areas, columns, g('default', ''),
                g('available', None), g('types', None))
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
