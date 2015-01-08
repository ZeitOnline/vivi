import zeit.cms.content.sources
import zeit.imp.interfaces
import zope.interface


class PossibleScale(object):

    zope.interface.implements(zeit.imp.interfaces.IPossibleScale)


class ScaleSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.imp'
    config_url = 'scale-source'

    def getValues(self, context):
        xml = self._get_tree()
        for scale_node in xml.iterchildren('*'):
            scale = PossibleScale()
            scale.width = scale_node.get('width')
            scale.height = scale_node.get('height')
            scale.title = scale_node.get('title')
            scale.name = scale_node.get('name')
            if self.isAvailable(scale_node, context):
                yield scale


class Color(object):

    zope.interface.implements(zeit.imp.interfaces.IColor)


class ColorSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.imp'
    config_url = 'color-source'

    def getValues(self, context):
        xml = self._get_tree()
        for node in xml.iterchildren('*'):
            color = Color()
            color.title = node.get('title')
            color.color = node.get('color')
            if self.isAvailable(node, context):
                yield color
