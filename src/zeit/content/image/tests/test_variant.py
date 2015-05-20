from zeit.cms.checkout.helper import checked_out
from zeit.content.image.interfaces import IVariants
import zeit.cms.testing
import zeit.content.image.testing
import zope.interface.verify


class VariantTraversal(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(VariantTraversal, self).setUp()
        self.group = zeit.content.image.testing.create_image_group()

    def test_variants_provides_mapping_interface(self):
        zope.interface.verify.verifyObject(IVariants, IVariants(self.group))

    def test_acess_variants_dict_entries_as_objects(self):
        with checked_out(self.group) as co:
            co.variants = {
                'square': {'focus_x': 0.5, 'focus_y': 0.5}
            }
        variant = IVariants(self.group)['square']
        self.assertEqual(0.5, variant.focus_x)
