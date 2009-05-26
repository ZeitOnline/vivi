# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.contextual
import zope.interface


class ITeaserBlockLayout(zope.interface.Interface):
    """Layout of a teaser block."""

    id = zope.schema.ASCIILine(title=u'Id used in xml to identify layout')
    title = zope.schema.TextLine(title=u'Human readable title.')

    image_pattern = zope.schema.ASCIILine(
        title=u'A match for the image to use in this layout.')


class ITeaserBarLayout(zope.interface.Interface):
    """Layout of a TeaserBar."""

    id = zope.schema.ASCIILine(title=u'Id used in xml to identify layout')
    title = zope.schema.TextLine(title=u'Human readable title.')

    blocks = zope.schema.Int(
        title=u'The number of blocks allowed by this layout.')


class BlockLayout(object):

    zope.interface.implements(ITeaserBlockLayout)

    def __init__(self, id, title, image_pattern=None,
                 area=None):
        self.id = id
        self.title = title
        self.image_pattern = image_pattern
        self.area = area


# XXX the image formats need to be set correctly, but we don't know them, yet.
TEASER_BLOCK = [
    BlockLayout('leader',
                u'Großer Teaser mit Bild und Teaserliste',
                '450x200', area='lead-1'),
    BlockLayout('leader-upright',
                u'Großer Teaser mit Hochkant-Bild und Teaserliste'
                '450x200', area='lead-1'),
    BlockLayout('buttons',
                u'Kleiner Teaser mit kleinem Bild und Teaserliste',
                '140x140', area='lead'),
    BlockLayout('two-side-by-side',
                u'Zwei kleine Teaser mit Bild',
                '140x140', area='informatives'),
    BlockLayout('large',
                u'Großer Teaser mit Bild und Teaserliste',
                '140x140', area='informatives'),
    BlockLayout('ressort',
                u'Ressort Teaser mit Teaserliste',
                '140x140', area='teaser-mosaic'),
]


# Aufmacher:Block:Großer Teaser mit 2 Spalten
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


class TeaserBlockLayoutSource(LayoutSource):

    def getValues(self, context):
        # Avoid circular import
        from zeit.content.cp.interfaces import IArea, ILead
        area = IArea(context)
        areas = [area.__name__]
        if ILead.providedBy(area):
            position = area.keys().index(context.__name__)
            if position == 0:
                areas.append('lead-1')
            else:
                areas.append('lead-x')
        return [layout for layout in TEASER_BLOCK
                if layout.area in areas]


class TeaserBarLayoutSource(LayoutSource):

    def getValues(self, context):
        return TEASER_BAR


def get_layout(id):
    for layout in TEASER_BLOCK + TEASER_BAR:
        if layout.id == id:
            return layout
