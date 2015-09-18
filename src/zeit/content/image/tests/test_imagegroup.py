from zeit.content.image.testing import create_image_group_with_master_image
from zeit.content.image.testing import create_local_image
import mock
import zeit.cms.testing
import zeit.content.image.testing
import zope.traversing.api


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

    def test_getitem_raises_keyerror_if_variant_does_not_exist(self):
        with self.assertRaises(KeyError):
            self.group['nonexistent']

    def test_variant_url_returns_path_with_size_if_given(self):
        self.assertEqual('/group/square__200x200', self.group.variant_url(
            'square', 200, 200))

    def test_variant_url_returns_path_without_size_if_none_given(self):
        self.assertEqual('/group/square', self.group.variant_url('square'))

    def test_returns_image_for_variant_with_size(self):
        self.assertEqual(
            (200, 200), self.group['square__200x200'].getImageSize())

    def test_ignores_invalid_size(self):
        self.assertEqual(
            (1536, 1536), self.group['square__0x200'].getImageSize())
        self.assertEqual(
            (1536, 1536), self.group['square__-1x200'].getImageSize())

    def test_dav_content_with_same_name_is_preferred(self):
        self.assertEqual((1536, 1536), self.group['square'].getImageSize())
        self.group['square'] = zeit.content.image.testing.create_local_image(
            'new-hampshire-450x200.jpg')
        self.assertEqual((450, 200), self.group['square'].getImageSize())

    def test_thumbnails_create_variants_from_smaller_master_image(self):
        self.assertEqual((1536, 1536), self.group['square'].getImageSize())
        thumbnails = zeit.content.image.interfaces.IThumbnails(self.group)
        self.assertEqual((750, 750), thumbnails['square'].getImageSize())

    def test_thumbnail_source_is_created_on_add(self):
        self.assertIn('thumbnail-source-master-image.jpg', self.group)

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


class SpoofProtectionTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(SpoofProtectionTest, self).setUp()
        self.group = create_image_group_with_master_image()
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.image')
        config['variant-secret'] = 'secret'

    def test_no_signature_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.group['square']
        with self.assertRaises(KeyError):
            self.group['square__200x200']

    def test_invalid_signature_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.group['square__invalid']
        with self.assertRaises(KeyError):
            self.group['square__200x200__invalid']

    def test_valid_signature_returns_image(self):
        path = self.group.variant_url('square')
        image = zope.traversing.api.traverse(self.repository, path[1:])
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))

        path = self.group.variant_url('square', 200, 200)
        image = zope.traversing.api.traverse(self.repository, path[1:])
        self.assertTrue(zeit.content.image.interfaces.IImage.providedBy(image))
