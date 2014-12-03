# coding: utf8
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.contextual
import zeit.cms.content.sources
import zeit.edit.interfaces
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
    default = zope.schema.Bool(
        title=u"True if this is the default for an area/region")


class ITeaserBarLayout(zope.interface.Interface):
    """Layout of a TeaserBar."""

    id = zope.schema.ASCIILine(title=u'Id used in xml to identify layout')
    title = zope.schema.TextLine(title=u'Human readable title.')

    blocks = zope.schema.Int(
        title=u'The number of blocks allowed by this layout.')


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


MAX_TEASER_BAR_BLOCKS = 4


class BarLayout(object):

    zope.interface.implements(ITeaserBarLayout)

    def __init__(self, id, title, blocks):
        self.id = id
        self.title = title
        self.blocks = blocks

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, BarLayout) and self.id == other.id


# XXX We need to hard-code this, because at import-time, when the default value
# is set on the interface, there's no product config yet, so we cannot use
# get_bar_layout().
DEFAULT_BAR_LAYOUT = BarLayout(
    'normal', 'Ressort Teaser mit Teaserliste', MAX_TEASER_BAR_BLOCKS)


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
        from zeit.content.cp.interfaces import ILead  # Avoid circular import

        if context is None:
            return True

        area = zeit.edit.interfaces.IArea(context)
        section = zeit.content.cp.interfaces.ISection(context)
        areas = [area.__name__, section.__name__]
        if ILead.providedBy(area):
            try:
                position = area.keys().index(context.__name__)
            except ValueError:  # Not in list
                position = 0
            if position == 0:
                areas.append('lead-1')
            else:
                areas.append('lead-x')
        return value.areas.intersection(areas)

TEASERBLOCK_LAYOUTS = TeaserBlockLayoutSource()


class TeaserBarLayoutSource(
        LayoutSourceBase, zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'bar-layout-source'
    attribute = 'id'

    def getValues(self, context):
        tree = self._get_tree()
        result = [DEFAULT_BAR_LAYOUT]
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            result.append(BarLayout(
                node.get(self.attribute),
                self._get_title_for(node),
                int(node.get('blocks', MAX_TEASER_BAR_BLOCKS))))
        return result

TEASERBAR_LAYOUTS = TeaserBarLayoutSource()


def get_layout(id):
    for layout in list(TEASERBLOCK_LAYOUTS(None)):
        if layout.id == id:
            return layout


def get_bar_layout(id):
    for layout in list(TEASERBAR_LAYOUTS(None)):
        if layout.id == id:
            return layout
