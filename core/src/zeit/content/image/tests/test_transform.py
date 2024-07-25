from pprint import pformat
import importlib.resources
import io

import PIL.Image
import PIL.ImageDraw

from zeit.content.image.variant import Variant
import zeit.content.image.interfaces
import zeit.content.image.testing


class CreateVariantImageTest(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
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
        with image.open('w') as f:
            pil_image.save(f, 'PNG')
        return image

    ascii_to_color = {
        ' ': (255, 255, 255, 255),
        'x': (0, 0, 0, 255),
        '/': (0, 0, 0, 0),
        'r': (255, 0, 0, 255),
        'g': (0, 255, 0, 255),
        'b': (0, 0, 255, 255),
    }
    color_to_ascii = {value: key for key, value in ascii_to_color.items()}

    def draw_image(self, pixels):
        width = len(pixels[0])
        height = len(pixels)
        image = PIL.Image.new('RGBA', (width, height), (255, 255, 255, 255))
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
        with image.open('r') as f:
            pil_image = PIL.Image.open(f)
        width, height = pil_image.size
        result = []
        for y in range(height):
            line = []
            for x in range(width):
                pixel = (pil_image.getpixel((x, y)) + (255,))[:4]
                line.append(self.color_to_ascii[pixel])
            result.append(''.join(line))
        return result

    def assertImage(self, pixels, image):
        actual = self.to_ascii(image)
        message = 'Expected:\n%s\n\nGot:\n%s' % (pformat(pixels), pformat(actual))
        self.assertEqual(pixels, actual, message)

    def test_fits_larger_side_of_mask_to_image_size(self):
        variant = Variant(id='square', focus_x=0.5, focus_y=0.5, zoom=1, aspect_ratio='1:1')
        image = self.transform.create_variant_image(variant)
        self.assertEqual((8, 8), image.getImageSize())

    def test_does_not_exceed_maximum_size(self):
        variant = Variant(id='square', focus_x=0.5, focus_y=0.5, zoom=1, aspect_ratio='1:1')
        self.transform.MAXIMUM_IMAGE_SIZE = 5
        image = self.transform.create_variant_image(variant, size=(10, 10))
        self.assertEqual((5, 5), image.getImageSize())

    def test_focus_point_after_crop_has_same_relative_position_as_before(self):
        variant = Variant(
            id='square', focus_x=5.0 / 16, focus_y=3.0 / 8, zoom=1, aspect_ratio='1:1'
        )
        self.assertImage(
            [
                '        ',
                '        ',
                '  x     ',
                '        ',
                '        ',
                '        ',
                '        ',
                '        ',
            ],
            self.transform.create_variant_image(variant),
        )

    def test_zoom_scales_image_and_respects_focus_point(self):
        variant = Variant(
            id='square', focus_x=5.0 / 16, focus_y=3.0 / 8, zoom=0.5, aspect_ratio='1:1'
        )
        self.assertImage(
            [
                '    ',
                ' x  ',
                '    ',
                '    ',
            ],
            self.transform.create_variant_image(variant),
        )

    def test_target_size_repositions_result_inside_variant_ratio(self):
        variant = Variant(id='wide', focus_x=5.0 / 16, focus_y=3.0 / 8, zoom=1, aspect_ratio='8:1')
        self.assertImage(
            [
                '  x     ',
                '        ',
            ],
            self.transform.create_variant_image(variant, (8, 2)),
        )

    def test_ratio_original_uses_ratio_of_source_image(self):
        variant = Variant(
            id='original', focus_x=5.0 / 16, focus_y=3.0 / 8, zoom=0.5, aspect_ratio='original'
        )
        self.assertImage(
            ['        ', '  x     ', '        ', '        '],
            self.transform.create_variant_image(variant),
        )

    def test_image_enhancements_are_applied_and_change_image(self):
        # Brightness of 0.0 makes image black
        variant = Variant(
            id='square',
            focus_x=5.0 / 16,
            focus_y=3.0 / 8,
            zoom=1,
            aspect_ratio='2:1',
            brightness=0.0,
        )
        self.assertImage(
            [
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
            ],
            self.transform.create_variant_image(variant),
        )

    def test_image_for_default_ignores_cropping_but_applies_brightness(self):
        """Apply no cropping to use the default variant image as master in UI."""
        # Create image group with b/w image that is equal to the image which is
        # generated during setUp
        self.group = zeit.content.image.testing.create_image_group_with_master_image(
            importlib.resources.files(__package__) / 'Black-White.PNG'
        )

        # Set zoom < 1, which would usually result in cropping,
        # also set brightness to test image enhancements
        self.group.variants = {
            'default': {'focus_x': 1, 'focus_y': 1, 'zoom': 0.5, 'brightness': 0.0}
        }

        # Result image is not cropped, i.e. still 16x8 in size
        # and is black due to brightness of 0.0
        self.variants = zeit.content.image.interfaces.IVariants(self.group)
        self.assertImage(
            [
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxx',
            ],
            self.transform.create_variant_image(self.variants['default']),
        )

    def test_all_image_enhancements_are_applied_to_variant_image(self):
        from unittest.mock import patch

        import PIL.Image

        variant = Variant(
            id='square',
            focus_x=0.5,
            focus_y=0.5,
            zoom=1,
            aspect_ratio='2:1',
            brightness=0.1,
            contrast=0.2,
            saturation=0.3,
            sharpness=0.4,
        )

        # Prepare side effect to return the image given to Image Enhancement
        def return_image(degenerated_image, original_image, alpha):
            return original_image

        with patch.object(PIL.Image, 'blend', wraps=return_image) as blend:
            self.transform.create_variant_image(variant)

        factors = [list(x)[0][2] for x in blend.call_args_list]
        self.assertEqual(4, blend.call_count)
        self.assertEqual([0.1, 0.2, 0.3, 0.4], sorted(factors))

    def test_variant_fill_color_is_ignored_if_image_has_no_alpha(self):
        img = zeit.content.image.testing.create_local_image(
            'Opaque.PNG', 'zeit.content.image', 'tests'
        )
        transform = zeit.content.image.interfaces.ITransform(img)
        variant = Variant(id='square', focus_x=0.5, focus_y=0.5, zoom=1, aspect_ratio='1:1')

        self.assertImage(
            [
                '        ',
                '        ',
                '        ',
                '        ',
                '        ',
                '        ',
                '        ',
                '        ',
            ],
            transform.create_variant_image(variant, fill_color='ff0000'),
        )

    def test_variant_fill_color_is_applied_if_image_has_alpha_channel(self):
        img = zeit.content.image.testing.create_local_image(
            'Frame.PNG', 'zeit.content.image', 'tests'
        )
        transform = zeit.content.image.interfaces.ITransform(img)
        variant = Variant(id='square', focus_x=0.5, focus_y=0.5, zoom=1, aspect_ratio='1:1')

        self.assertImage(
            [
                '        ',
                ' rrrrrr ',
                ' rrrrrr ',
                ' rrrrrr ',
                ' rrrrrr ',
                ' rrrrrr ',
                ' rrrrrr ',
                '        ',
            ],
            transform.create_variant_image(variant, fill_color='ff0000'),
        )

    def test_invalid_variant_size_should_not_raise_pil_systemerror(self):
        variant = Variant(id='wide', focus_x=0.5, focus_y=0.5, zoom=1, aspect_ratio='1:1')
        image = self.transform.create_variant_image(variant, size=(0, 0), fill_color='ffffff')
        self.assertEqual((8, 8), image.getImageSize())

    def test_encoder_parameters_are_configurable(self):
        group = zeit.content.image.testing.create_image_group_with_master_image()
        transform = zeit.content.image.interfaces.ITransform(group['master-image.jpg'])
        highquality = io.BytesIO()
        img = transform.image.copy()
        img.thumbnail((200, 200))
        img.save(highquality, 'JPEG', quality=75)
        highquality.seek(0)
        configured = transform.thumbnail(200, 200)

        self.assertLess(len(configured.open().read()), len(highquality.read()))
