from pprint import pformat
from zeit.content.image.variant import Variant
import PIL.Image
import PIL.ImageDraw
import zeit.cms.testing
import zeit.content.image.interfaces
import zeit.content.image.testing


class CreateVariantImageTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(CreateVariantImageTest, self).setUp()
        self.transform = self._transform(
            'xx        xxxxxx',
            'xx        xxxxxx',
            'xx  x     xxxxxx',
            'xx        xxxxxx',
            'xx        xxxxxx',
            'xx        xxxxxx',
            'xx        xxxxxx',
            'xx        xxxxxx',
        )

    def create_image(self, pil_image):
        image = zeit.content.image.image.LocalImage()
        image.mimeType = 'image/png'
        pil_image.save(image.open('w'), 'PNG')
        return image

    ascii_to_color = {
        ' ': (255, 255, 255, 255),
        'x': (0, 0, 0, 255)
    }
    color_to_ascii = {value: key for key, value in ascii_to_color.items()}

    def draw_image(self, pixels):
        width = len(pixels[0])
        height = len(pixels)
        image = PIL.Image.new('RGB', (width, height), (255, 255, 255))
        draw = PIL.ImageDraw.ImageDraw(image)
        for x in range(width):
            for y in range(height):
                draw.point((x, y), self.ascii_to_color[pixels[y][x]])
        return image

    def _transform(self, *pixels):
        pil_image = self.draw_image(pixels)
        image = self.create_image(pil_image)
        transform = zeit.content.image.interfaces.ITransform(image)
        return transform

    def to_ascii(self, image):
        pil_image = PIL.Image.open(image.open('r'))
        width, height = pil_image.size
        result = []
        for y in range(height):
            line = []
            for x in range(width):
                line.append(self.color_to_ascii[pil_image.getpixel((x, y))])
            result.append(''.join(line))
        return result

    def assertImage(self, pixels, image):
        actual = self.to_ascii(image)
        message = (
            'Expected:\n%s\n\nGot:\n%s' % (pformat(pixels), pformat(actual)))
        self.assertEqual(pixels, actual, message)

    def test_fits_larger_side_of_mask_to_image_size(self):
        variant = Variant(
            id='square', focus_x=0.5, focus_y=0.5, zoom=1, aspect_ratio='1:1')
        image = self.transform.create_variant_image(variant)
        self.assertEqual((8, 8), image.getImageSize())

    def test_focus_point_after_crop_has_same_relative_position_as_before(self):
        variant = Variant(id='square', focus_x=5.0 / 16, focus_y=3.0 / 8,
                          zoom=1, aspect_ratio='1:1')
        self.assertImage([
            '        ',
            '        ',
            '  x     ',
            '        ',
            '        ',
            '        ',
            '        ',
            '        ',
        ], self.transform.create_variant_image(variant))

    def test_zoom_scales_image_and_respects_focus_point(self):
        variant = Variant(id='square', focus_x=5.0 / 16, focus_y=3.0 / 8,
                          zoom=0.5, aspect_ratio='1:1')
        self.assertImage([
            '    ',
            ' x  ',
            '    ',
            '    ',
        ], self.transform.create_variant_image(variant))

    def test_target_size_repositions_result_inside_variant_ratio(self):
        variant = Variant(id='wide', focus_x=5.0 / 16, focus_y=3.0 / 8,
                          zoom=1, aspect_ratio='8:1')
        self.assertImage([
            '  x     ',
            '        ',
        ], self.transform.create_variant_image(variant, (8, 2)))

    def test_image_enhancements_are_applied_and_change_image(self):
        variant = Variant(id='square', focus_x=5.0 / 16, focus_y=3.0 / 8,
                          zoom=1, aspect_ratio='2:1', brightness=0.0)
        self.assertImage([
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
        ], self.transform.create_variant_image(variant))
