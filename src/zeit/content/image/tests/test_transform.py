from zeit.content.image.variant import Variant
import zeit.cms.testing
import zeit.content.image.interfaces
import zeit.content.image.testing


class CropTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(CropTest, self).setUp()
        self.transform = zeit.content.image.interfaces.ITransform(
            self.repository['2006']['DSC00109_2.JPG'])

    def test_fits_larger_side_of_mask_to_image_size(self):
        variant = Variant(focus_x=0.5, focus_y=0.5, ratio='16:9')
        image = self.transform.crop(variant)
        self.assertEqual((2048, 1152), image.getImageSize())
