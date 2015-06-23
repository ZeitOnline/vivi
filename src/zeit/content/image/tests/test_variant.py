from zeit.content.image.interfaces import IVariants
import mock
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

    def test_can_access_small_variant_via_name_and_size(self):
        variant = IVariants(self.group).get_by_size('cinema__200x100')
        self.assertEqual('cinema-small', variant.id)

    def test_defaults_to_variant_without_size_limitation_if_size_too_big(self):
        variant = IVariants(self.group).get_by_size('cinema__9999x9999')
        self.assertEqual('cinema-large', variant.id)

    def test_invalid_name_returns_none(self):
        self.assertEqual(
            None, IVariants(self.group).get_by_size('foobarbaz__9999x9999'))

    def test_no_size_matches_returns_none(self):
        from zeit.content.image.variant import Variants, Variant
        with mock.patch.object(Variants, 'values', return_value=[
                Variant(name='foo', id='small', max_size='100x100')]):
            self.assertEqual(
                None, IVariants(self.group).get_by_size('foo__9999x9999'))
