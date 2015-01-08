import zeit.cms.content.sources
import zope.interface
import zope.security.proxy


class ITeaserBlockLayout(zope.interface.Interface):
    """Layout of a teaser block."""

    id = zope.schema.ASCIILine(title=u'Id used in xml to identify layout')
    title = zope.schema.TextLine(title=u'Human readable title.')
    image_pattern = zope.schema.ASCIILine(
        title=u'A match for the image to use in this layout.')
    image_positions = zope.schema.Bool(
        title=u'Show image for each teaser, allow individual positions '
        'to be suppressed')
    columns = zope.schema.Int(
        title=u'Columns',
        min=1,
        max=2,
        default=1)
    areas = zope.schema.Set(
        title=u'Widths of areas where this layout is allowed')
    default = zope.schema.Bool(
        title=u"True if this is the default for an area")


class IAreaLayout(zope.interface.Interface):
    """Layout of an Area."""

    id = zope.schema.ASCIILine(title=u'Id used in xml to identify layout')
    title = zope.schema.TextLine(title=u'Human readable title.')


class BlockLayout(object):

    zope.interface.implements(ITeaserBlockLayout)

    def __init__(self, id, title, image_pattern=None,
                 areas=None, columns=1, default=False, image_positions=False):
        self.id = id
        self.title = title
        self.image_pattern = image_pattern
        self.image_positions = image_positions
        self.areas = frozenset(areas)
        self.columns = columns
        self.default = default

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, BlockLayout) and self.id == other.id


class AreaLayout(object):

    zope.interface.implements(IAreaLayout)

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, AreaLayout) and self.id == other.id


class AreaConfig(object):

    def __init__(self, id, title, width):
        self.id = id
        self.title = title
        self.width = width

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, AreaConfig) and self.id == other.id


# XXX We need to hard-code this, because at import-time, when the default value
# is set on the interface, there's no product config yet, so we cannot use
# get_area_layout().
DEFAULT_AREA_LAYOUT = AreaLayout('normal', 'Ressort Teaser mit Teaserliste')


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

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            g = node.get
            areas = g('areas')
            areas = areas.split()
            columns = g('columns', 1)
            if columns:
                columns = int(columns)
            default = g('default', '').lower() == 'true'
            image_positions = g('image_positions', '').lower() == 'true'
            result.append(BlockLayout(
                node.get(self.attribute), self._get_title_for(node),
                g('image_pattern'), areas, columns, default, image_positions))
        return result

    def _get_title_for(self, node):
        return unicode(node.get('title'))

    def filterValue(self, context, value):
        if context is None:
            return True
        area = zeit.content.cp.interfaces.IArea(context)
        return area.width in value.areas

TEASERBLOCK_LAYOUTS = TeaserBlockLayoutSource()


class AreaLayoutSource(
        LayoutSourceBase, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'bar-layout-source'  # BBB
    attribute = 'id'

    def getValues(self, context):
        tree = self._get_tree()
        result = [DEFAULT_AREA_LAYOUT]
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            result.append(AreaLayout(
                node.get(self.attribute),
                self._get_title_for(node)))
        return result

AREA_LAYOUTS = AreaLayoutSource()


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
                node.get('width')))
        return result

AREA_CONFIGS = AreaConfigSource()


def get_layout(id):
    for layout in list(TEASERBLOCK_LAYOUTS(None)):
        if layout.id == id:
            return layout


def get_area_layout(id):
    for layout in list(AREA_LAYOUTS(None)):
        if layout.id == id:
            return layout
