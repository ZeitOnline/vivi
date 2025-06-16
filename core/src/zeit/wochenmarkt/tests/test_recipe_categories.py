# -*- coding: utf-8 -*-
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


class TestRecipeCategories(zeit.wochenmarkt.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.categories_source = zeit.wochenmarkt.sources.recipeCategoriesSource(None).factory

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

    def test_flagged_categories_are_not_found(self):
        categories = zeit.wochenmarkt.sources.recipeCategoriesSource.factory.search('T')
        self.assertEqual(
            [
                'huelsenfruechte',
                'pastagerichte',
                'salat',
                'vegane-rezepte',
                'vegetarische-rezepte',
                'wurstiges',
            ],
            sorted([x.id for x in categories]),
        )
