# -*- coding: utf-8 -*-
import lxml.etree

from zeit.wochenmarkt.categories import RecipeCategories
import zeit.wochenmarkt.sources
import zeit.wochenmarkt.testing


class TestRecipeCategoriesWhitelist(zeit.wochenmarkt.testing.FunctionalTestCase):
    def test_category_should_be_found_by_id(self):
        categories = zeit.wochenmarkt.sources.recipeCategoriesSource(None).factory._values()
        assert 'Pizza' == categories.get('pizza').name

    def test_autocomplete_should_be_available_for_categories(self):
        source = zeit.wochenmarkt.sources.recipeCategoriesSource(None).factory
        result = source.search('B')
        assert 2 == len(result)
        names = []
        for item in result:
            names.append(item.name)
        assert 'Barbecue' in names


class TestRecipeCategories(
    zeit.wochenmarkt.testing.FunctionalTestCase, zeit.wochenmarkt.testing.RecipeCategoriesHelper
):
    def setUp(self):
        super().setUp()
        self.categories_source = zeit.wochenmarkt.sources.recipeCategoriesSource(None).factory

    def get_content(self):
        class Content:
            categories = RecipeCategories()
            xml = lxml.etree.fromstring('<article><head/></article>')

        return Content()

    def test_set_should_add_new_categories(self):
        categories = self.setup_categories('summer', 'pizza')
        summer = categories['summer']
        pizza = categories['pizza']
        content = self.get_content()
        content.categories = [summer, pizza]
        result = content.categories
        self.assertEqual(['summer', 'pizza'], [x.code for x in result])

    def test_set_should_write_categories_to_xml_head(self):
        categories = self.setup_categories('summer')
        summer = categories['summer']
        content = self.get_content()
        content.categories = [summer]
        self.assertEllipsis(
            '<recipe_categories...><category code="summer"/>...',
            lxml.etree.tostring(content.xml.find('head/recipe_categories'), encoding=str),
        )

    def test_removing_all_categories_should_leave_no_trace(self):
        categories = self.setup_categories('summer')
        summer = categories['summer']
        content = self.get_content()
        content.categories = [summer]
        self.assertEqual(1, len(content.xml.xpath('//recipe_categories')))
        content.categories = []
        self.assertEqual(0, len(content.xml.xpath('//recipe_categories')))

    def test_unavailable_categories_should_just_be_skipped(self):
        categories = self.setup_categories('servomotoren', 'pizza')
        servomotoren = categories['servomotoren']
        pizza = categories['pizza']
        content = self.get_content()
        content.categories = [servomotoren, pizza]
        result = content.categories
        self.assertEqual(['pizza'], [x.code for x in result])

    def test_for_diets_vegetarian(self):
        diets = {'vegetarian'}
        category = self.categories_source.for_diets(diets)
        assert category.id == 'vegetarische-rezepte'

    def test_for_diets_vegetarian_and_vegan(self):
        diets = {'vegetarian', 'vegan'}
        category = self.categories_source.for_diets(diets)
        assert category.id == 'vegetarische-rezepte'

    def test_for_diets_vegan_only(self):
        diets = {'vegan'}
        category = self.categories_source.for_diets(diets)
        assert category.id == 'vegane-rezepte'

    def test_for_diets_no_match(self):
        diets = {'omnivore'}
        category = self.categories_source.for_diets(diets)
        assert category is None

    def test_for_diets_conflicting_diets(self):
        diets = {'omnivore', 'vegan'}
        category = self.categories_source.for_diets(diets)
        assert category is None

    def test_for_diets_nothing_given(self):
        diets = {}
        category = self.categories_source.for_diets(diets)
        assert category is None

    def test_for_diets_precedence_prioritizes(self):
        diets = {
            'frutarian': 'frutarian',
            'vegan,frutarian': 'vegane-rezepte',
            'vegetarian,frutarian': 'vegetarische-rezepte',
            'frutarian,vegetarian,vegan': 'vegetarische-rezepte',
        }
        for diet, expected_category in diets.items():
            category = self.categories_source.for_diets(set(diet.split(',')))
            assert category, f'Should be {expected_category} with diets {diet}'
            assert category.id == expected_category, (
                f'Should be {expected_category} with diets {diet}'
            )

    def test_flagged_categories_are_not_found(self):
        categories = zeit.wochenmarkt.sources.recipeCategoriesSource.factory.search('T')
        self.assertEqual(
            [
                'frutarian',
                'huelsenfruechte',
                'pastagerichte',
                'salat',
                'vegane-rezepte',
                'vegetarische-rezepte',
                'wurstiges',
            ],
            sorted([x.id for x in categories]),
        )
