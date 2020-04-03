# -*- coding: utf-8 -*-

from ..ingredients import Ingredients
import zope.component
import zeit.cms.recipe.interfaces
import zeit.cms.recipe.testing


class TestIngredients(zeit.cms.recipe.testing.FunctionalTestCase):
    """Testing ..ingredients.Ingredients"""

    def test_get_basmati_from_ingredients_xml(self):
        ingredients = zope.component.getUtility(
            zeit.cms.recipe.interfaces.IIngredients)._load()
        basmati = dict(ingredients.items()).get('basmatireis')
        assert 'Basmatireis' == basmati.name
        assert 'other' == basmati.category

    def test_get_ingredient_by_id(self):
        calamari = zope.component.getUtility(
            zeit.cms.recipe.interfaces.IIngredients).get('calamari')
        assert 'Calamari' == calamari.name
        assert 'fish' == calamari.category

    def test_ingredients_with_category_meat(self):
        meat_ingredients = zope.component.getUtility(
            zeit.cms.recipe.interfaces.IIngredients).category('meat')
        assert 2 == len(meat_ingredients)

    def test_search_for_ingredient(self):
        result = zope.component.getUtility(
            zeit.cms.recipe.interfaces.IIngredients).search('B')
        assert 6 == len(result)
        names = []
        for item in result:
            names.append(item.name)
        assert u'Brathähnchen' in names

    def test_search_only_in_category_chicken(self):
        chicken = zope.component.getUtility(
            zeit.cms.recipe.interfaces.IIngredients).category('chicken', 'B')
        assert 1 == len(chicken)
        assert u'Brathähnchen' == chicken[0].name

