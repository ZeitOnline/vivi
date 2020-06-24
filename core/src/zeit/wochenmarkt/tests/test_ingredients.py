# -*- coding: utf-8 -*-

import zope.component
import zeit.wochenmarkt.interfaces
import zeit.wochenmarkt.testing


class TestIngredients(zeit.wochenmarkt.testing.FunctionalTestCase):
    """Testing ..ingredients.Ingredients"""

    def test_ingredient_should_be_found_through_xml(self):
        ingredients = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredientsWhitelist)._load()
        basmati = dict(ingredients.items()).get('basmatireis')
        assert 'Basmatireis' == basmati.name
        assert 'other' == basmati.category
        assert ['Reis', 'Basmati'] == basmati.qwords
        assert basmati.qwords_category is None
        assert 'Basmatireis' == basmati.singular
        assert 'Basmatireis' == basmati.plural

    def test_ingredient_should_be_found_by_id(self):
        calamari = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredientsWhitelist).get('calamari')
        assert 'Calamari' == calamari.name
        assert 'fish' == calamari.category
        assert ['Tintenfisch', 'Kalamar'] == calamari.qwords
        assert ['Fisch', ' Meeresfrüchte'] == calamari.qwords_category

    def test_ingredients_should_be_found_by_category(self):
        meat_ingredients = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredientsWhitelist).category('meat')
        assert 2 == len(meat_ingredients)

    def test_autocomplete_should_be_available_for_ingredients(self):
        result = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredientsWhitelist).search('B')
        assert 6 == len(result)
        names = []
        for item in result:
            names.append(item.name)
        assert u'Brathähnchen' in names

    def test_ingredients_should_be_found_through_multiple_criteria(self):
        chicken = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredientsWhitelist).category(
                'chicken', 'B')
        assert 1 == len(chicken)
        assert u'Brathähnchen' == chicken[0].name
