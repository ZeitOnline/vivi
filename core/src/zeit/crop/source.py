import zeit.cms.content.sources
import zeit.crop.interfaces
import zope.interface


@zope.interface.implementer(zeit.crop.interfaces.IPossibleScale)
class PossibleScale:
    pass


class ScaleSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.crop'
    config_url = 'scale-source'
    default_filename = 'scales.xml'

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


@zope.interface.implementer(zeit.crop.interfaces.IColor)
class Color:
    pass


class ColorSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.crop'
    config_url = 'color-source'
    default_filename = 'imp-colors.xml'

    def getValues(self, context):
        xml = self._get_tree()
        for node in xml.iterchildren('*'):
            color = Color()
            color.title = node.get('title')
            color.color = node.get('color')
            if self.isAvailable(node, context):
                yield color
