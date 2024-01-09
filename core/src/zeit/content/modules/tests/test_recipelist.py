from unittest import mock

import lxml.objectify

from zeit.cms.interfaces import ValidationError
from zeit.content.modules.interfaces import validate_servings
from zeit.content.modules.recipelist import Ingredient
import zeit.cms.testing
import zeit.content.modules.embed
import zeit.content.modules.testing


class RecipeListTest(
    zeit.content.modules.testing.FunctionalTestCase, zeit.content.modules.testing.IngredientsHelper
):
    def setUp(self):
        super().setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.recipelist.RecipeList(
            self.context, lxml.objectify.XML('<container/>')
        )

    def get_content(self):
        from lxml import objectify

        from zeit.content.modules.recipelist import RecipeList

        class Content:
            xml = objectify.fromstring('<recipelist/>')
            recipe_list = RecipeList(self.context, xml)

        return Content().recipe_list

    def test_title_should_be_stored_in_xml(self):
        self.module.title = 'banana'
        self.assertEqual(self.module.xml.xpath('//title'), ['banana'])

    def test_set_should_add_new_ingredients(self):
        ingredients = self.setup_ingredients('banana', 'milk')
        banana = ingredients['banana']
        milk = ingredients['milk']
        self.module.ingredients = [banana, milk]
        self.assertEqual(['banana', 'milk'], ([x.code for x in self.module.ingredients]))

    def test_set_should_allow_duplicate_ingredients(self):
        ingredients = self.setup_ingredients('banana')
        banana = ingredients['banana']
        self.module.ingredients = [banana, banana]
        self.assertEqual(['banana', 'banana'], ([x.code for x in self.module.ingredients]))

    def test_set_should_write_ingredients_to_xml_head(self):
        ingredients = self.setup_ingredients('banana', 'milk')
        banana = ingredients['banana']
        milk = ingredients['milk']
        self.module.ingredients = [banana, milk]
        xml = self.module.xml.ingredient
        self.assertEqual('banana', xml.get('code'))
        self.assertEqual('2', xml.get('amount'))
        self.assertEqual('g', xml.get('unit'))
        self.assertEqual('sautiert', xml.get('details'))

    def test_removing_all_ingredients_should_leave_no_trace(self):
        ingredients = self.setup_ingredients('banana')
        banana = ingredients['banana']
        self.module.ingredients = [banana]
        self.assertEqual(1, len(self.module.xml.xpath('//ingredient')))
        self.module.ingredients = []
        self.assertEqual(0, len(self.module.xml.xpath('//ingredient')))

    def test_unavailable_ingredients_should_just_be_skipped(self):
        ingredients = self.setup_ingredients('moepelspeck', 'banana')
        moepelspeck = ingredients['moepelspeck']
        banana = ingredients['banana']
        content = self.get_content()
        content.ingredients = [moepelspeck, banana]
        result = content.ingredients
        self.assertEqual(['banana'], [x.code for x in result])

    def test_incomplete_ingredients_should_be_skipped(self):
        # physalis is missing @plural
        ingredients = self.setup_ingredients('physalis', 'banana')
        physalis = ingredients['physalis']
        banana = ingredients['banana']
        content = self.get_content()
        content.ingredients = [physalis, banana]
        result = content.ingredients
        self.assertEqual(['banana'], [x.code for x in result])

    def test_servings_should_be_validated(self):
        assert validate_servings('1') is True
        assert validate_servings('1-2') is True
        assert validate_servings('9-12') is True
        assert validate_servings('10-12') is True
        assert validate_servings('100-225') is True

        with self.assertRaises(ValidationError):
            validate_servings('')
        with self.assertRaises(ValidationError):
            validate_servings('0')
        with self.assertRaises(ValidationError):
            validate_servings('1-2-3')
        with self.assertRaises(ValidationError):
            validate_servings('5-3')  # must not decrease
        with self.assertRaises(ValidationError):
            validate_servings('1-')
        with self.assertRaises(ValidationError):
            validate_servings('-2')
        with self.assertRaises(ValidationError):
            validate_servings('a')
        with self.assertRaises(ValidationError):
            validate_servings('1-a')

    def test_ingredients_should_receive_properties_from_whitelist(self):
        node = lxml.objectify.XML('<ingredient code="banana" amount="1" unit="kg"/>')
        ingredient = Ingredient(None, None).from_xml(node)
        assert ingredient.code == 'banana'
        assert ingredient.label == 'Banane'
        assert ingredient.plural == 'Bananen'

    def test_missing_xml_attributes_should_have_empty_string_as_default(self):
        node = lxml.objectify.XML('<ingredient code="banana" amount="1" unit="kg"/>')
        ingredient = Ingredient(None, None).from_xml(node)
        assert ingredient.code == 'banana'
        assert ingredient.details == ''  # not provided as xml attribute
