# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.basic
import zope.interface


class Layout(object):

    def __init__(self, id, title, image_pattern=None, blocks=None):
        self.id = id
        self.title = title
        self.image_pattern = image_pattern
        self.blocks = blocks


TEASER_BLOCK = [
    Layout('leader',
           u'Großer Teaser mit Bild und Teaserliste',
           image_pattern='450x200'),
    Layout('buttons',
           u'Kleiner Teaser mit kleinem Bild und Teaserliste',
           '140x140'),
]

TEASER_BAR = [
    Layout('normal',
           u'Ressort Teaser mit Teaserliste', blocks=4),
    Layout('mr',
           u'Ad-Medium Recangle', blocks=3),
    Layout('dmr',
           u'Double Ad-Medium Recangle', blocks=2)
]


class LayoutSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getTitle(self, value):
        return value.title

    def getToken(self, value):
        return value.id


class TeaserBlockLayoutSource(LayoutSource):

    def getValues(self):
        return TEASER_BLOCK


class TeaserBarLayoutSource(LayoutSource):

    def getValues(self):
        return TEASER_BAR


def get_layout(id):
    for layout in TEASER_BLOCK + TEASER_BAR:
        if layout.id == id:
            return layout
