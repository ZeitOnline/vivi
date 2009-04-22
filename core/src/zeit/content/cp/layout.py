# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.basic
import zope.interface
import zope.schema.interfaces


class Layout(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title


LAYOUTS = [
    Layout('leader', u'Großer Teaser mit Bild und Teaserliste'),
    Layout('buttons', u'Kleiner Teaser mit kleinem Bild und Teaserliste'),
]


class LayoutSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return LAYOUTS

    def getTitle(self, value):
        return value.title

    def getToken(self, value):
        return value.id
