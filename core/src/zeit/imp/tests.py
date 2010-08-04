# coding: utf8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image
import StringIO
import pkg_resources
import unittest
import zeit.cms.testing
import zeit.content.image.tests
import zeit.imp.interfaces
import zeit.imp.mask
import zeit.imp.source
import zope.app.testing.functional
import zope.interface.verify


product_config = """
<product-config zeit.imp>
    scale-source file://%s
    color-source file://%s
</product-config>
""" % (
    pkg_resources.resource_filename(__name__, 'scales.xml'),
    pkg_resources.resource_filename(__name__, 'colors.xml'))


imp_layer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class TestLayerMask(unittest.TestCase):

    def test_mask(self):
        # Create a 20x30 mask in an 150x100 image
        mask = zeit.imp.mask.Mask((150, 100), (20, 30))
        mask_data = mask.open('r').read()
        expected_data = pkg_resources.resource_string(
            __name__, 'test_mask.png')
        self.assertEquals(expected_data, mask_data,
                          "Mask doesn't match expected mask.")

    def test_mask_with_border(self):
        # Create a 20x30 mask in an 150x100 image
        mask = zeit.imp.mask.Mask((150, 100), (20, 30), border=(0, 0, 0))
        mask_data = mask.open('r').read()
        expected_data = pkg_resources.resource_string(
            __name__, 'test_mask_border.png')
        self.assertEquals(expected_data, mask_data,
                          "Mask doesn't match expected mask.")

    def test_mask_color(self):
        mask = zeit.imp.mask.Mask((100, 100), (100, 100), border=(255, 0, 0))
        image = PIL.Image.open(mask.open('r'))
        self.assertEquals((255, 0, 0, 255), image.getpixel((0, 0)))

    def test_rect_box(self):
        mask = zeit.imp.mask.Mask((150, 100), (20, 30))
        self.assertEquals(((65, 35), (85, 65)), mask._get_rect_box())


class TestSources(zope.app.testing.functional.BrowserTestCase):

    layer = imp_layer

    def test_scale_source(self):
        source = zeit.imp.source.ScaleSource()
        scales = list(source)
        self.assertEquals(7, len(scales))
        scale = scales[0]
        zope.interface.verify.verifyObject(
            zeit.imp.interfaces.IPossibleScale, scale)
        self.assertEquals('450x200', scale.name)
        self.assertEquals('450', scale.width)
        self.assertEquals('200', scale.height)
        self.assertEquals(u'Aufmacher groß (450×200)', scale.title)

    def test_color_source(self):
        source = zeit.imp.source.ColorSource()
        values = list(source)
        self.assertEquals(3, len(values))
        value = values[1]
        zope.interface.verify.verifyObject(zeit.imp.interfaces.IColor, value)
        self.assertEquals('schwarzer Rahmen (1 Pixel)', value.title)
        self.assertEquals('#000000', value.color)


class TestCrop(zope.app.testing.functional.BrowserTestCase):

    layer = imp_layer

    def setUp(self):
        super(TestCrop, self).setUp()
        self.setSite(self.getRootFolder())
        self.group = (
            zeit.content.image.tests.create_image_group_with_master_image())
        self.crop = zeit.imp.interfaces.ICropper(self.group)

    def tearDown(self):
        self.setSite(None)
        super(TestCrop, self).tearDown()

    def get_histogram(self, image):
        histogram = image.histogram()
        r, g, b = histogram[:256], histogram[256:512], histogram[512:]
        return r, g, b

    def test_invalid_filter_raises_valueerror(self):
        self.assertRaises(ValueError, self.crop.add_filter, 'foo', 1)

    def test_brightness_filter(self):
        # Factor 0 produces a solid black image. The histogram has only black
        # in it
        self.crop.add_filter('brightness', 0)
        image = self.crop.crop(200, 200, 0, 0, 200, 200)
        r, g, b = self.get_histogram(image)
        self.assertEquals(40000, r[0])
        self.assertEquals(40000, g[0])
        self.assertEquals(40000, b[0])
        self.assertEquals(0, sum(r[1:]))
        self.assertEquals(0, sum(g[1:]))
        self.assertEquals(0, sum(b[1:]))

    def test_color_filter(self):
        # Factor 0 gives a black and white image, so the channels are equal
        self.crop.add_filter('color', 0)
        image = self.crop.crop(200, 200, 0, 0, 200, 200)
        r, g, b = self.get_histogram(image)
        self.assertEquals(r, g)
        self.assertEquals(r, b)

    def test_contrast_filter(self):
        # A contrast factor of 0 produces a solid gray image:
        self.crop.add_filter('contrast', 0)
        image = self.crop.crop(200, 200, 0, 0, 200, 200)
        r, g, b = self.get_histogram(image)
        self.assertEquals(40000, sum(r))
        self.assertEquals(40000, sum(g))
        self.assertEquals(40000, sum(b))
        self.assertEquals(40000, r[156])
        self.assertEquals(40000, g[156])
        self.assertEquals(40000, b[156])

    def test_sharpness_filter(self):
        # Testing the sharpnes is not quite trival. We just check that the
        # histograms have changed:
        self.crop.add_filter('sharpness', 0)
        image = self.crop.crop(200, 200, 0, 0, 200, 200)
        r_smooth, g, b = self.get_histogram(image)

        # Create the sharp image now
        self.crop.filters[:] = []
        self.crop.add_filter('sharpness', 1000)
        image = self.crop.crop(200, 200, 0, 0, 200, 200)
        r_sharp, g, b = self.get_histogram(image)
        self.assertNotEqual(r_smooth, r_sharp)

    def test_store(self):
        self.crop.crop(200, 200, 0, 0, 200, 200)
        image = zeit.imp.interfaces.IStorer(self.group).store(
            'foo', self.crop.pil_image)
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))
        self.assertEquals(['group-foo.jpg', 'master-image.jpg'],
                          self.group.keys())

    def test_border_applied_after_filters(self):
        # The border must be applied after the filters. To verify this we
        # create an image with no contrast which is solid gray. The border adds
        # some black.
        self.crop.add_filter('contrast', 0)
        image = self.crop.crop(200, 200, 0, 0, 200, 200, border=(0, 0, 0))
        r, g, b = self.get_histogram(image)
        self.assertNotEquals(40000, r[156])
        self.assertNotEquals(40000, g[156])
        self.assertNotEquals(40000, b[156])
        self.assertNotEquals(0, r[0])
        self.assertNotEquals(0, g[0])
        self.assertNotEquals(0, b[0])

    def test_border_color(self):
        image = self.crop.crop(200, 200, 0, 0, 200, 200,
                               border=(127, 127, 127))
        self.assertEquals((127, 127, 127), image.getpixel((0,0)))

    def test_border_on_grayscale_image(self):
        self.group = (
            zeit.content.image.tests.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/grayscale.jpg')))
        crop = zeit.imp.interfaces.ICropper(self.group)
        # The following used to fail with TypeError: an integer is required
        image = self.crop.crop(200, 200, 0, 0, 200, 200,
                               border=(127, 127, 127))

    def test_cmyk_converted_to_rgb(self):
        self.group = (
            zeit.content.image.tests.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/cmyk.jpg')))
        crop = zeit.imp.interfaces.ICropper(self.group)
        image = self.crop.crop(200, 200, 0, 0, 200, 200,
                               border=(127, 127, 127))
        self.assertEquals('RGB', image.mode)

    def test_palette_converted_to_rgb(self):
        self.group = (
            zeit.content.image.tests.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/palette.gif')))
        crop = zeit.imp.interfaces.ICropper(self.group)
        image = self.crop.crop(200, 200, 0, 0, 200, 200,
                               border=(127, 127, 127))
        self.assertEquals('RGB', image.mode)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLayerMask))
    suite.addTest(unittest.makeSuite(TestSources))
    suite.addTest(unittest.makeSuite(TestCrop))
    return suite
