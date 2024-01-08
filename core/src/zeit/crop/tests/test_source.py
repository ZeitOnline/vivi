import zope.interface.verify

import zeit.crop.source
import zeit.crop.testing


class TestSources(zeit.crop.testing.FunctionalTestCase):
    def test_scale_source(self):
        source = zeit.crop.source.ScaleSource()(None)
        scales = list(source)
        self.assertEqual(7, len(scales))
        scale = scales[0]
        zope.interface.verify.verifyObject(zeit.crop.interfaces.IPossibleScale, scale)
        self.assertEqual('450x200', scale.name)
        self.assertEqual('450', scale.width)
        self.assertEqual('200', scale.height)
        self.assertEqual('Aufmacher groß (450×200)', scale.title)

    def test_color_source(self):
        source = zeit.crop.source.ColorSource()(None)
        values = list(source)
        self.assertEqual(3, len(values))
        value = values[1]
        zope.interface.verify.verifyObject(zeit.crop.interfaces.IColor, value)
        self.assertEqual('schwarzer Rahmen (1 Pixel)', value.title)
        self.assertEqual('#000000', value.color)
