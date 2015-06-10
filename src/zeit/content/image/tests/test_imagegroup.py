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
