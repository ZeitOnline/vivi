import PIL.Image
import pkg_resources
import unittest
import zeit.cms.testing
import zeit.content.image.testing
import zeit.crop.interfaces
import zeit.crop.mask
import zeit.crop.source
import zeit.crop.testing


class TestLayerMask(unittest.TestCase):

    mask_colors = {(200, 200, 200, 220): 'x',
                   (255, 0, 0, 0): ' ',
                   (0, 0, 0, 255): '#',
                   (0, 255, 0, 128): ' '}

    def assert_mask(self, expected, mask):
        with mask.open('r') as f:
            mask_image = PIL.Image.open(f)
            mask_image.load()
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
        mask = zeit.crop.mask.Mask((10, 7), (6, 3), cross_size=0)
        expected = ['xxxxxxxxxx',
                    'xxxxxxxxxx',
                    'xx      xx',
                    'xx      xx',
                    'xx      xx',
                    'xxxxxxxxxx',
                    'xxxxxxxxxx']
        self.assert_mask(expected, mask)

    def test_border_should_be_inside_given_mask_size(self):
        mask = zeit.crop.mask.Mask((20, 20), (10, 8), border=(0, 0, 0),
                                   cross_size=0)
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
        mask = zeit.crop.mask.Mask((100, 100), (100, 100), border=(255, 0, 0))
        with mask.open('r') as f:
            image = PIL.Image.open(f)
            image.load()
        self.assertEqual((255, 0, 0, 255), image.getpixel((0, 0)))

    def test_rect_box_should_match_given_mask_size(self):
        mask = zeit.crop.mask.Mask((150, 100), (20, 30))
        (x1, y1), (x2, y2) = mask._get_rect_box()
        # There is a rather missleading comment in the PIL documentation which
        # indicates that we need to pass 1px less than the expected size:
        # "Note that the second coordinate pair defines a point just outside
        # the rectangle, also when the rectangle is not filled."
        self.assertEqual(19, x2 - x1)
        self.assertEqual(29, y2 - y1)


class TestCrop(zeit.crop.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image())
        self.crop = zeit.crop.interfaces.ICropper(self.group)

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
        self.assertEqual(40000, r[0])
        self.assertEqual(40000, g[0])
        self.assertEqual(40000, b[0])
        self.assertEqual(0, sum(r[1:]))
        self.assertEqual(0, sum(g[1:]))
        self.assertEqual(0, sum(b[1:]))

    def test_color_filter(self):
        # Factor 0 gives a black and white image, so the channels are equal
        self.crop.add_filter('color', 0)
        image = self.crop.crop(200, 200, 0, 0, 200, 200)
        r, g, b = self.get_histogram(image)
        self.assertEqual(r, g)
        self.assertEqual(r, b)

    def test_contrast_filter(self):
        # A contrast factor of 0 produces a solid gray image:
        self.crop.add_filter('contrast', 0)
        image = self.crop.crop(200, 200, 0, 0, 200, 200)
        r, g, b = self.get_histogram(image)
        self.assertEqual(40000, sum(r))
        self.assertEqual(40000, sum(g))
        self.assertEqual(40000, sum(b))
        self.assertEqual(40000, r[100])
        self.assertEqual(40000, g[100])
        self.assertEqual(40000, b[100])

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
        image = zeit.crop.interfaces.IStorer(self.group).store(
            'foo', self.crop.pil_image)
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))
        self.assertIn('group-foo.jpg', self.group)

    def test_border_applied_after_filters(self):
        # The border must be applied after the filters. To verify this we
        # create an image with no contrast which is solid gray. The border adds
        # some black.
        self.crop.add_filter('contrast', 0)
        image = self.crop.crop(200, 200, 0, 0, 200, 200, border=(0, 0, 0))
        r, g, b = self.get_histogram(image)
        self.assertNotEqual(40000, r[156])
        self.assertNotEqual(40000, g[156])
        self.assertNotEqual(40000, b[156])
        self.assertNotEqual(0, r[0])
        self.assertNotEqual(0, g[0])
        self.assertNotEqual(0, b[0])

    def test_border_color(self):
        image = self.crop.crop(200, 200, 0, 0, 200, 200,
                               border=(127, 127, 127))
        self.assertEqual((127, 127, 127), image.getpixel((0, 0)))

    def test_border_on_grayscale_image(self):
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/grayscale.jpg')))
        # The following used to fail with TypeError: an integer is required
        crop = zeit.crop.interfaces.ICropper(self.group)
        crop.crop(200, 200, 0, 0, 200, 200, border=(127, 127, 127))

    def test_cmyk_converted_to_rgb(self):
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/cmyk.jpg')))
        crop = zeit.crop.interfaces.ICropper(self.group)
        image = crop.crop(200, 200, 0, 0, 200, 200, border=(127, 127, 127))
        self.assertEqual('RGB', image.mode)

    def test_palette_converted_to_rgb(self):
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/palette.gif')))
        crop = zeit.crop.interfaces.ICropper(self.group)
        image = crop.crop(200, 200, 0, 0, 200, 200, border=(127, 127, 127))
        self.assertEqual('RGB', image.mode)

    def test_png_converted_to_rgba(self):
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image(
                pkg_resources.resource_filename(
                    __name__, 'testdata/transparent.png')))
        crop = zeit.crop.interfaces.ICropper(self.group)
        image = crop.crop(200, 200, 0, 0, 200, 200, border=(127, 127, 127))
        self.assertEqual('RGBA', image.mode)
        # Check that the alpha channel survives the cropping intact.
        self.assertEqual((183, 255, 159, 64), image.getpixel((100, 25)))
