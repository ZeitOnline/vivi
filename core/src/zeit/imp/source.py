# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.sources
import zeit.imp.interfaces
import zope.interface


class PossibleScale(object):

    zope.interface.implements(zeit.imp.interfaces.IPossibleScale)


class ScaleSource(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.imp'
    config_url = 'scale-source'

    def getValues(self):
        xml = self._get_tree()
        for scale_node in xml.iterchildren():
            scale = PossibleScale()
            scale.width = scale_node.get('width')
            scale.height = scale_node.get('height')
            scale.title = scale_node.get('title')
            scale.name = scale_node.get('name')
            yield scale
