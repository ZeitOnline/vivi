import sys

import zope.interface.verify

from zeit.content.image.interfaces import IVariants
import zeit.content.image.testing


class VariantTraversal(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.group = zeit.content.image.testing.create_image_group()

    def test_variants_provides_mapping_interface(self):
        zope.interface.verify.verifyObject(IVariants, IVariants(self.group))

    def test_access_variants_dict_entries_as_objects(self):
        self.group.variants = {'square': {'focus_x': 0.1, 'focus_y': 0.1, 'zoom': 0.3}}
        variant = IVariants(self.group)['square']
        self.assertEqual(0.1, variant.focus_x)
        self.assertEqual(0.1, variant.focus_y)
        self.assertEqual(0.3, variant.zoom)

    def test_variant_with_settings_gets_missing_values_from_XML(self):
        self.group.variants = {'square': {'focus_x': 0.1, 'focus_y': 0.1, 'zoom': 0.3}}
        variant = IVariants(self.group)['square']
        self.assertEqual('1:1', variant.aspect_ratio)

    def test_variant_with_settings_gets_missing_values_from_default_variant(
        self,
    ):  # this is important for new default values in the future
        self.group.variants = {'square': {'focus_x': 0.1, 'focus_y': 0.1}}
        variant = IVariants(self.group)['square']
        self.assertEqual(1, variant.zoom)

    def test_variant_without_settings_returns_default_settings(self):
        self.group.variants = {'default': {'focus_x': 0.1, 'focus_y': 0.1, 'zoom': 0.5}}
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


class VariantProperties(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.group = zeit.content.image.testing.create_image_group_with_master_image()

    @property
    def variants(self):
        return IVariants(self.group)

    def test_ratio_is_float_representation_of_aspect_ratio(self):
        self.assertEqual('1:1', self.variants['square'].aspect_ratio)
        self.assertEqual(1, self.variants['square'].ratio)
        self.assertEqual('16:9', self.variants['cinema-small'].aspect_ratio)
        self.assertEqual(16.0 / 9.0, self.variants['cinema-small'].ratio)

    def test_default_has_no_ratio(self):
        self.assertEqual(None, self.variants['default'].aspect_ratio)
        self.assertEqual(None, self.variants['default'].ratio)

    def test_setting_aspect_ratio_to_original_will_use_ratio_from_master_image(self):
        self.group.variants = {'square': {'aspect_ratio': 'original'}}
        self.assertEqual('original', self.variants['square'].aspect_ratio)
        self.assertEqual(None, self.variants['square'].ratio)

    def test_max_width_retrieves_value_from_max_size(self):
        self.assertEqual(sys.maxsize, self.variants['square'].max_width)
        self.group.variants = {'square': {'max_size': '100x200'}}
        self.assertEqual(100, self.variants['square'].max_width)

    def test_max_height_retrieves_value_from_max_size(self):
        self.assertEqual(sys.maxsize, self.variants['square'].max_height)
        self.group.variants = {'square': {'max_size': '100x200'}}
        self.assertEqual(200, self.variants['square'].max_height)

    def test_default_is_recognized_as_default_but_square_is_not(self):
        self.assertEqual(True, self.variants['default'].is_default)
        self.assertEqual(False, self.variants['square'].is_default)

    def test_relative_path_variants_link_to_thumbnail_of_that_variant(self):
        self.assertEqual('thumbnails/default', self.variants['default'].relative_image_path)
        self.assertEqual('thumbnails/square', self.variants['square'].relative_image_path)

    def test_relative_path_contains_max_size_to_distinguish_variant_sizes(self):
        self.assertEqual(
            'thumbnails/cinema__320x180', self.variants['cinema-small'].relative_image_path
        )
