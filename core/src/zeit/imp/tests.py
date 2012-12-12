# coding: utf8
# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image
import pkg_resources
import unittest
import zeit.cms.testing
import zeit.content.image.testing
import zeit.imp.interfaces
import zeit.imp.mask
import zeit.imp.source
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

    mask_colors = {(200, 200, 200, 220): 'x',
                   (255, 0, 0, 0): ' ',
                   (0, 0, 0, 255): '#'}

    def assert_mask(self, expected, mask):
        mask_image = PIL.Image.open(mask.open('r'))
        width, height = mask_image.size
        got = []
        for y in range(height):
            line = []
            for x in range(width):
                line.append(self.mask_colors[mask_image.getpixel((x, y))])
            got.append(''.join(line))
        error_message = (
            'The computed mask did not match the expected.\n'
            'Expected:\n%s\n\nGot:\n%s' % ('\n'.join(expected),
                                           '\n'.join(got)))
        self.assertEqual(expected, got, error_message)


    def test_mask_should_have_correct_size(self):
        # Create a 20x30 mask in an 150x100 image
        mask = zeit.imp.mask.Mask((10, 7), (6, 3))
        expected = ['xxxxxxxxxx',
                    'xxxxxxxxxx',
                    'xx      xx',
                    'xx      xx',
                    'xx      xx',
                    'xxxxxxxxxx',
                    'xxxxxxxxxx']
        self.assert_mask(expected, mask)


    def test_border_should_be_inside_given_mask_size(self):
        mask = zeit.imp.mask.Mask((20, 20), (10, 8), border=(0, 0, 0))
        expected = ['xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxx##########xxxxx',
                    'xxxxx#        #xxxxx',
                    'xxxxx#        #xxxxx',
                    'xxxxx#        #xxxxx',
                    'xxxxx#        #xxxxx',
                    'xxxxx#        #xxxxx',
                    'xxxxx#        #xxxxx',
                    'xxxxx##########xxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx',
                    'xxxxxxxxxxxxxxxxxxxx']
        self.assert_mask(expected, mask)

    def test_given_border_colour_should_be_used(self):
        mask = zeit.imp.mask.Mask((100, 100), (100, 100), border=(255, 0, 0))
        image = PIL.Image.open(mask.open('r'))
        self.assertEquals((255, 0, 0, 255), image.getpixel((0, 0)))

    def test_rect_box_should_match_given_mask_size(self):
        mask = zeit.imp.mask.Mask((150, 100), (20, 30))
        (x1, y1), (x2, y2) = mask._get_rect_box()
        # There is a rather missleading comment in the PIL documentation which
        # indicates that we need to pass 1px less than the expected size:
        # "Note that the second coordinate pair defines a point just outside
        # the rectangle, also when the rectangle is not filled."
        self.assertEqual(19, x2 - x1)
        self.assertEqual(29, y2 - y1)


class TestSources(zeit.cms.testing.FunctionalTestCase):

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


class TestCrop(zeit.cms.testing.FunctionalTestCase):

    layer = imp_layer

    def setUp(self):
        super(TestCrop, self).setUp()
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image())
        self.crop = zeit.imp.interfaces.ICropper(self.group)

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
        self.assertEquals(40000, r[99])
        self.assertEquals(40000, g[99])
        self.assertEquals(40000, b[99])

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
            zeit.content.image.testing.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/grayscale.jpg')))
        crop = zeit.imp.interfaces.ICropper(self.group)
        # The following used to fail with TypeError: an integer is required
        image = self.crop.crop(200, 200, 0, 0, 200, 200,
                               border=(127, 127, 127))

    def test_cmyk_converted_to_rgb(self):
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/cmyk.jpg')))
        crop = zeit.imp.interfaces.ICropper(self.group)
        image = self.crop.crop(200, 200, 0, 0, 200, 200,
                               border=(127, 127, 127))
        self.assertEquals('RGB', image.mode)

    def test_palette_converted_to_rgb(self):
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image(
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
