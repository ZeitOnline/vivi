# coding: utf-8
from zeit.content.image.testing import create_image_group_with_master_image
from zeit.content.image.testing import create_local_image
import mock
import PIL
import zeit.cms.testing
import zeit.content.image.testing


class ImageGroupTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(ImageGroupTest, self).setUp()
        self.group = create_image_group_with_master_image()

    def test_getitem_returns_dav_content(self):
        image = self.group['master-image.jpg']
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))

    def test_getitem_creates_image_from_variant_if_no_dav_content(self):
        image = self.group['square']
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))
        self.assertEqual(self.group, image.__parent__)
        self.assertEqual('square', image.__name__)
        self.assertEqual('http://xml.zeit.de/group/square', image.uniqueId)

    def test_getitem_uses_mapping_for_legacy_names_and_adjusts_size(self):
        image = self.group['master-image-540x304.jpg']
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))
        self.assertEqual((300, 200), image.getImageSize())

    def test_getitem_raises_keyerror_for_unmapped_legacy_names(self):
        with self.assertRaises(KeyError):
            self.group['master-image-111x222.jpg']

    def test_getitem_raises_keyerror_for_wrongly_mapped_legacy_names(self):
        with self.assertRaises(KeyError):
            self.group['master-image-148x84.jpg']

    def test_getitem_returns_materialized_files_for_new_syntax(self):
        self.group['master-image-540x304.jpg'] = create_local_image(
            'obama-clinton-120x120.jpg')
        image = self.group['540x304']
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))
        self.assertEqual((120, 120), image.getImageSize())

    def test_getitem_can_scale_materialized_files_for_new_syntax(self):
        master = PIL.Image.open(self.group['540x304__80x80'].open())
        master_sample = master.getpixel((40, 20))
        self.group['master-image-540x304.jpg'] = create_local_image(
            'obama-clinton-120x120.jpg')
        materialized = PIL.Image.open(self.group['540x304__80x80'].open())
        materialized_sample = materialized.getpixel((40, 20))
        self.assertNotEqual(master_sample, materialized_sample)
        self.assertEqual((80, 80), materialized.size)

    def test_getitem_can_scale_materialized_files_with_legacy_name(self):
        master = PIL.Image.open(self.group['540x304__80x80'].open())
        master_sample = master.getpixel((40, 20))
        self.group['master-image-540x304.jpg'] = create_local_image(
            'obama-clinton-120x120.jpg')
        materialized = PIL.Image.open(
            self.group['master-image-540x304__80x80'].open())
        materialized_sample = materialized.getpixel((40, 20))
        self.assertNotEqual(master_sample, materialized_sample)
        self.assertEqual((80, 80), materialized.size)

    def test_getitem_handles_viewport_modifier(self):
        with self.assertNothingRaised():
            self.group['square__mobile']

    def test_getitem_defines_no_variant_source_for_materialized_files(self):
        """It raises AttributeError when asked for `variant_source`.

        Since `variant_source` is used for testing only, we do not want to add
        it to `BaseImage`. Thus only variants created using
        `ImageGroupBase.create_variant_image` should have this attribute.

        """
        image = self.group['master-image.jpg']
        with self.assertRaises(AttributeError):
            image.variant_source

    def test_getitem_uses_primary_master_image_if_no_viewport_was_given(self):
        image = self.group['square']
        self.assertEqual('master-image.jpg', image.variant_source)

    def test_getitem_uses_primary_master_image_if_viewport_not_configured(
            self):
        """Default configuration only includes `desktop`, but not `mobile`."""
        image = self.group['square__mobile']
        self.assertEqual('master-image.jpg', image.variant_source)

    def test_getitem_chooses_master_image_using_given_viewport(self):
        """Uses master-image for desktop and master-image-mobile for mobile."""
        self.group['master-image-mobile.jpg'] = create_local_image(
            'obama-clinton-120x120.jpg')
        with mock.patch(
                'zeit.content.image.imagegroup.ImageGroupBase.master_images',
                new_callable=mock.PropertyMock) as master_images:
            master_images.return_value = (
                ('desktop', 'master-image.jpg'),
                ('mobile', 'master-image-mobile.jpg'))
            self.assertEqual(
                'master-image.jpg',
                self.group['square__desktop'].variant_source)
            self.assertEqual(
                'master-image-mobile.jpg',
                self.group['square__mobile'].variant_source)

    def test_getitem_ignores_master_image_for_viewport_if_nonexistent(self):
        with mock.patch(
                'zeit.content.image.imagegroup.ImageGroupBase.master_images',
                new_callable=mock.PropertyMock) as master_images:
            master_images.return_value = (('desktop', 'nonexistent.jpg'),)
            self.assertEqual(
                'master-image.jpg',
                self.group['square__desktop'].variant_source)

    def test_getitem_raises_keyerror_if_variant_does_not_exist(self):
        with self.assertRaises(KeyError):
            self.group['nonexistent']

    def test_variant_url_returns_path_with_size_if_given(self):
        self.assertEqual('/group/square__200x200', self.group.variant_url(
            'square', 200, 200))

    def test_variant_url_returns_path_without_size_if_none_given(self):
        self.assertEqual('/group/square', self.group.variant_url('square'))

    def test_variant_url_handles_non_ascii(self):
        group = self.repository[u'groüp'] = self.group
        self.assertEqual(u'/groüp/square', group.variant_url('square'))

    def test_returns_image_for_variant_with_size(self):
        self.assertEqual(
            (200, 200), self.group['square__200x200'].getImageSize())

    def test_invalid_size_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.group['square__0x200']

        with self.assertRaises(KeyError):
            self.group['square__-1x200']

    def test_variant_url_returns_path_with_fill_color_if_given(self):
        self.assertEqual(
            '/group/square__200x200__0000ff', self.group.variant_url(
                'square', 200, 200, '0000ff'))

    def test_dav_content_with_same_name_is_preferred(self):
        self.assertEqual((1536, 1536), self.group['square'].getImageSize())
        self.group['square'] = zeit.content.image.testing.create_local_image(
            'new-hampshire-450x200.jpg')
        self.assertEqual((450, 200), self.group['square'].getImageSize())

    def test_thumbnails_create_variants_from_smaller_master_image(self):
        self.assertEqual((1536, 1536), self.group['square'].getImageSize())
        thumbnails = zeit.content.image.interfaces.IThumbnails(self.group)
        self.assertEqual((750, 750), thumbnails['square'].getImageSize())

    def test_can_access_small_variant_via_name_and_size(self):
        variant = self.group.get_variant_by_size('cinema__200x100')
        self.assertEqual('cinema-small', variant.id)

    def test_defaults_to_variant_without_size_limitation_if_size_too_big(self):
        variant = self.group.get_variant_by_size('cinema__9999x9999')
        self.assertEqual('cinema-large', variant.id)

    def test_invalid_names_should_return_none(self):
        self.assertEqual(
            None, self.group.get_variant_by_size('foobarbaz__9999x9999'))
        self.assertEqual(
            None, self.group.get_variant_by_size('cinema__200xfoo'))
        self.assertEqual(
            None, self.group.get_variant_by_size('cinema__800x'))

    def test_no_size_matches_returns_none(self):
        from zeit.content.image.variant import Variants, Variant
        with mock.patch.object(Variants, 'values', return_value=[
                Variant(name='foo', id='small', max_size='100x100')]):
            self.assertEqual(
                None, self.group.get_variant_by_size('foo__9999x9999'))

    def test_master_image_is_None_if_no_master_images_defined(self):
        group = zeit.content.image.imagegroup.ImageGroup()
        self.assertEqual(None, group.master_image)

    def test_master_image_retrieves_first_image_from_master_images(self):
        group = zeit.content.image.imagegroup.ImageGroup()
        group.master_images = (('viewport', 'master.png'),)
        self.assertEqual('master.png', group.master_image)

    def test_master_image_is_retrieved_from_DAV_properties_for_bw_compat(self):
        from zeit.content.image.interfaces import IMAGE_NAMESPACE
        group = zeit.content.image.imagegroup.ImageGroup()
        properties = zeit.connector.interfaces.IWebDAVReadProperties(group)
        properties[('master_image', IMAGE_NAMESPACE)] = 'master.png'
        self.assertEqual('master.png', group.master_image)

    def test_master_image_for_viewport_ignores_if_nonexistent(self):
        with mock.patch(
                'zeit.content.image.imagegroup.ImageGroupBase.master_images',
                new_callable=mock.PropertyMock) as master_images:
            master_images.return_value = (('desktop', 'nonexistent.jpg'),)
            self.assertEqual(
                'master-image.jpg',
                self.group.master_image_for_viewport('desktop').__name__)

    def test_device_pixel_ratio_affects_image_size(self):
        self.assertEqual(
            (600, 320), self.group['cinema__300x160__scale_2.0'].getImageSize())
        self.assertEqual(
            (180, 96), self.group['cinema__300x160__scale_0.6'].getImageSize())
        self.assertEqual(
            (675, 360), self.group['cinema__300x160__scale_2.25'].getImageSize())

    def test_unallowed_device_pixel_ratio_is_ignored(self):
        self.assertEqual(
            (300, 160), self.group['cinema__300x160__scale_0.2'].getImageSize())
        self.assertEqual(
            (300, 160), self.group['cinema__300x160__scale_99999'].getImageSize())

    def test_scaled_image_get_zoom_from_non_scaled_size(self):
        self.group.variants = {
            'cinema-small': {'zoom': 0.3, 'max_size': '300x160'},
            'cinema-large': {'zoom': 1.0, 'max_size': '600x320'}
        }
        self.assertEqual(
            0.3, self.group.get_variant_by_size('cinema__300x160__scale_2.0').zoom)
        self.assertEqual(
            0.3, self.group.get_variant_by_size('cinema__300x160').zoom)
        self.assertEqual(
            1.0, self.group.get_variant_by_size('cinema__600x320').zoom)


class ThumbnailsTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        from ..imagegroup import Thumbnails
        super(ThumbnailsTest, self).setUp()
        self.group = create_image_group_with_master_image()
        self.thumbnails = Thumbnails(self.group)

    def test_uses_master_image_for_thumbnails(self):
        self.assertEqual(
            self.group['master-image.jpg'],
            self.thumbnails.master_image('square'))

    def test_uses_image_defined_for_viewport_desktop_when_given(self):
        self.assertEqual(
            self.group['master-image.jpg'],
            self.thumbnails.master_image('square__desktop'))

    def test_uses_image_defined_for_viewport_mobile_when_given(self):
        self.group['master-image-mobile.jpg'] = create_local_image(
            'obama-clinton-120x120.jpg')
        with mock.patch(
                'zeit.content.image.imagegroup.ImageGroupBase.master_images',
                new_callable=mock.PropertyMock) as master_images:
            master_images.return_value = (
                ('desktop', 'master-image.jpg'),
                ('mobile', 'master-image-mobile.jpg'))
            self.assertEqual(
                self.group['master-image-mobile.jpg'],
                self.thumbnails.master_image('square__mobile'))
