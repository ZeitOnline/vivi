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

    def test_access_variants_dict_entries_as_objects(self):
        self.group.variants = {
            'square': {'focus_x': 0.1, 'focus_y': 0.1, 'zoom': 0.3}
        }
        variant = IVariants(self.group)['square']
        self.assertEqual(0.1, variant.focus_x)
        self.assertEqual(0.1, variant.focus_y)
        self.assertEqual(0.3, variant.zoom)

    def test_variant_with_settings_gets_missing_values_from_XML(self):
        self.group.variants = {
            'square': {'focus_x': 0.1, 'focus_y': 0.1, 'zoom': 0.3}
        }
        variant = IVariants(self.group)['square']
        self.assertEqual('1:1', variant.aspect_ratio)

    def test_variant_with_settings_gets_missing_values_from_default_variant(
            self):  # this is important for new default values in the future
        self.group.variants = {
            'square': {'focus_x': 0.1, 'focus_y': 0.1}
        }
        variant = IVariants(self.group)['square']
        self.assertEqual(1, variant.zoom)

    def test_variant_without_settings_returns_default_settings(self):
        self.group.variants = {
            'default': {'focus_x': 0.1, 'focus_y': 0.1, 'zoom': 0.5}
        }
        variant = IVariants(self.group)['square']
        self.assertEqual(0.1, variant.focus_x)
        self.assertEqual(0.1, variant.focus_y)
        self.assertEqual(0.5, variant.zoom)

    def test_variant_without_settings_without_default_returns_config(self):
        variant = IVariants(self.group)['square']
        self.assertEqual(0.5, variant.focus_x)
        self.assertEqual(0.5, variant.focus_y)
        self.assertEqual(1, variant.zoom)

    def test_variant_should_be_comparable_by_their_respective_ids(self):
        group1 = zeit.content.image.testing.create_image_group()
        variant1 = IVariants(group1)['square']
        group2 = zeit.content.image.testing.create_image_group()
        variant2 = IVariants(group2)['square']
        self.assertEqual(variant1, variant2)

    def test_source_should_parse_additional_settings(self):
        variant = IVariants(self.group)['cinema-small']
        self.assertEqual(1600, variant.fallback_width)
        self.assertEqual(900, variant.fallback_height)
        self.assertEqual(320, variant.max_width)
        self.assertEqual(180, variant.max_height)
