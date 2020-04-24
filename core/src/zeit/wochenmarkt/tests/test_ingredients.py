# -*- coding: utf-8 -*-

import zope.component
import zeit.wochenmarkt.interfaces
import zeit.wochenmarkt.testing


class TestIngredients(zeit.wochenmarkt.testing.FunctionalTestCase):
    """Testing ..ingredients.Ingredients"""

    def test_ingredient_should_be_found_through_xml(self):
        ingredients = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredients)._load()
        basmati = dict(ingredients.items()).get('basmatireis')
        assert 'Basmatireis' == basmati.name
        assert 'other' == basmati.category

    def test_ingredient_should_be_found_by_id(self):
        calamari = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredients).get('calamari')
        assert 'Calamari' == calamari.name
        assert 'fish' == calamari.category

    def test_ingredients_should_be_found_by_category(self):
        meat_ingredients = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredients).category('meat')
        assert 2 == len(meat_ingredients)

    def test_autocomplete_should_be_available_for_ingredients(self):
        result = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredients).search('B')
        assert 6 == len(result)
        names = []
        for item in result:
            names.append(item.name)
        assert u'Brathähnchen' in names

    def test_ingredients_should_be_found_through_multiple_criteria(self):
        chicken = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredients).category('chicken', 'B')
        assert 1 == len(chicken)
        assert u'Brathähnchen' == chicken[0].name
