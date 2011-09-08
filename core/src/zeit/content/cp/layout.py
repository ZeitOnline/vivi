# coding: utf8
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.contextual
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


# Aufmacher:Block:Großer Teaser mit Bildergalerie und Teaserliste
# Aufmacher:Block:Großer Teaser mit Video statt Bild und Teaserliste




class BarLayout(object):

    zope.interface.implements(ITeaserBarLayout)

    def __init__(self, id, title, blocks):
        self.id = id
        self.title = title
        self.blocks = blocks



MAX_TEASER_BAR_BLOCKS = 4


TEASER_BAR = [
    BarLayout('normal',
              u'Ressort Teaser mit Teaserliste', blocks=4),
    BarLayout('mr',
              u'Ad-Medium Recangle', blocks=2),
    BarLayout('dmr',
              u'Double Ad-Medium Recangle', blocks=1)
]


class LayoutSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):

    def getTitle(self, context, value):
        return value.title

    def getToken(self, context, value):
        return value.id


class AllTeaserBlockLayoutSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'block-layout-source'

    def getValues(self):
        xml = self._get_tree()
        result = []
        for layout in xml['layout']:
            g = layout.get
            areas = g('areas')
            areas = areas.split()
            columns = g('columns', 1)
            if columns:
                columns = int(columns)
            default = g('default', '').lower() == 'true'
            result.append(BlockLayout(
                g('id'), g('title'), g('image_pattern'), areas, columns,
                default))
        return result


class TeaserBlockLayoutSource(LayoutSource):

    def getValues(self, context):
        # Avoid circular import
        from zeit.content.cp.interfaces import IArea, ILead
        area = IArea(context)
        areas = [area.__name__]
        if ILead.providedBy(area):
            try:
                position = area.keys().index(context.__name__)
            except ValueError:  # Not in list
                position = 0
            if position == 0:
                areas.append('lead-1')
            else:
                areas.append('lead-x')
        return [layout for layout in AllTeaserBlockLayoutSource()
                if layout.areas.intersection(areas)]


class TeaserBarLayoutSource(LayoutSource):

    def getValues(self, context):
        return TEASER_BAR


def get_layout(id):
    for layout in list(AllTeaserBlockLayoutSource()):
        if layout.id == id:
            return layout


def get_bar_layout(id):
    for layout in TEASER_BAR:
        if layout.id == id:
            return layout
