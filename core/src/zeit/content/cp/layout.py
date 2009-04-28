# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.basic
import zope.interface
import zope.schema.interfaces


class Layout(object):

    def __init__(self, id, title, image_pattern=None):
        self.id = id
        self.title = title
        self.image_pattern = image_pattern


LAYOUTS = [
    Layout('leader',
           u'Großer Teaser mit Bild und Teaserliste',
           image_pattern='450x200'),
    Layout('buttons',
           u'Kleiner Teaser mit kleinem Bild und Teaserliste',
           '140x140'),
]


class LayoutSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return LAYOUTS

    def getTitle(self, value):
        return value.title

    def getToken(self, value):
        return value.id

def get_layout(id):
    for layout in LAYOUTS:
        if layout.id == id:
            return layout
