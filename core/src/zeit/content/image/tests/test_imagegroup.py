from zeit.content.image.testing import create_image_group_with_master_image
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

    def test_getitem_raises_keyerror_if_variant_does_not_exist(self):
        with self.assertRaises(KeyError):
            self.group['nonexistent']

    def test_getitem_raises_keyerror_if_no_master_image(self):
        group = zeit.content.image.testing.create_image_group()
        with self.assertRaises(KeyError):
            group['square']

    def test_variant_url_returns_path_with_size_if_given(self):
        self.assertEqual('/group/square__200x200', self.group.variant_url(
            'square', 200, 200))

    def test_variant_url_returns_path_without_size_if_none_given(self):
        self.assertEqual('/group/square', self.group.variant_url('square'))

    def test_returns_image_for_variant_with_size(self):
        self.assertEqual(
            (200, 200), self.group['square__200x200'].getImageSize())

    def test_dav_content_with_same_name_is_preferred(self):
        self.assertEqual((1536, 1536), self.group['square'].getImageSize())
        self.group['square'] = zeit.content.image.testing.create_local_image(
            'new-hampshire-450x200.jpg')
        self.assertEqual((450, 200), self.group['square'].getImageSize())

    def test_thumbnails_create_variants_from_smaller_master_image(self):
        self.assertEqual((1536, 1536), self.group['square'].getImageSize())
        thumbnails = zeit.content.image.interfaces.IThumbnails(self.group)
        self.assertEqual((750, 750), thumbnails['square'].getImageSize())
