import collections
import zc.sourcefactory.source
import zeit.cms.content.sources
import zope.interface
import zope.security.proxy


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
    default = zope.schema.Bool(
        title=u"True if this is the default for an area")


class BlockLayout(object):

    zope.interface.implements(ITeaserBlockLayout)

    def __init__(self, id, title, image_pattern=None,
                 areas=None, columns=1, default=False):
        self.id = id
        self.title = title
        self.image_pattern = image_pattern
        self.areas = frozenset(areas)
        self.columns = columns
        self.default = default

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, BlockLayout) and self.id == other.id


class RegionConfig(object):

    def __init__(self, id, title, kind, areas):
        self.id = id
        self.title = title
        self.kind = kind
        self.areas = areas

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, RegionConfig) and self.id == other.id


class AreaConfig(object):

    def __init__(self, id, title, kind):
        self.id = id
        self.title = title
        self.kind = kind

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, AreaConfig) and self.id == other.id


class LayoutSourceBase(object):

    def getTitle(self, context, value):
        return value.title

    def getToken(self, context, value):
        return value.id

    def isAvailable(self, node, context):
        # Avoid circular import
        from zeit.content.cp.interfaces import ICenterPage
        context = ICenterPage(context, None)
        if context is None:
            return True
        return super(LayoutSourceBase, self).isAvailable(node, context)


class TeaserBlockLayoutSource(
        LayoutSourceBase, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'block-layout-source'
    attribute = 'id'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        def find(self, id):
            return self.factory.find(self.context, id)

    def getValues(self, context):
        return self._values(context).values()

    def _values(self, context):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            g = node.get
            areas = g('areas')
            areas = areas.split()
            columns = g('columns', 1)
            if columns:
                columns = int(columns)
            default = self._is_default(node, context)
            id = node.get(self.attribute)
            result[id] = BlockLayout(
                id, self._get_title_for(node),
                g('image_pattern'), areas, columns, default)
        return result

    def find(self, context, id):
        value = self._values(context).get(id)
        if not value or not self.filterValue(context, value):
            return None
        return value

    def _is_default(self, node, context):
        if context is None:
            return False
        area = zeit.content.cp.interfaces.IArea(context)
        return area.kind in node.get('default', '')

    def _get_title_for(self, node):
        return unicode(node.get('title'))

    def filterValue(self, context, value):
        if context is None:
            return True
        area = zeit.content.cp.interfaces.IArea(context)
        return area.kind in value.areas

TEASERBLOCK_LAYOUTS = TeaserBlockLayoutSource()


class RegionConfigSource(
        LayoutSourceBase, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'region-config-source'

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            result.append(RegionConfig(
                node.get('id'),
                self._get_title_for(node),
                node.get('kind'),
                [{'kind': x.get('kind')} for x in node.iterchildren('area')]
            ))
        return result

    def _get_title_for(self, node):
        return unicode(node.get('title'))

REGION_CONFIGS = RegionConfigSource()


class AreaConfigSource(
        LayoutSourceBase, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'area-config-source'

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            result.append(AreaConfig(
                node.get('id'),
                self._get_title_for(node),
                node.get('kind')))
        return result

AREA_CONFIGS = AreaConfigSource()


def get_layout(id):
    return TEASERBLOCK_LAYOUTS(None).find(id)
