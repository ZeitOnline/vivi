# -*- coding: utf-8 -*-

import zope.component

import zeit.cms.testing
import zeit.wochenmarkt.interfaces
import zeit.wochenmarkt.testing


class TestIngredients(zeit.wochenmarkt.testing.FunctionalTestCase):
    """Testing ..ingredients.Ingredients"""

    def test_ingredient_should_be_found_through_xml(self):
        ingredients = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredientsWhitelist
        )._load()
        basmati = dict(ingredients.items()).get('basmatireis')
        assert 'Basmatireis' == basmati.name
        assert ['Reis', 'Basmati'] == basmati.qwords
        assert 'Basmatireis' == basmati.singular
        assert 'Basmatireis' == basmati.plural

    def test_ingredient_should_be_found_by_id(self):
        calamari = zope.component.getUtility(zeit.wochenmarkt.interfaces.IIngredientsWhitelist).get(
            'calamari'
        )
        assert 'Calamari' == calamari.name
        assert ['Tintenfisch', 'Kalamar'] == calamari.qwords

    def test_autocomplete_should_be_available_for_ingredients(self):
        result = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredientsWhitelist
        ).search('B')
        assert 8 == len(result)
        names = []
        for item in result:
            names.append(item.name)
        assert 'Brathähnchen' in names

    def test_ingredients_should_be_sorted_with_exact_match_leading(self):
        result = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IIngredientsWhitelist
        ).search('ei')
        assert ['Ei', 'Eis', 'Basmatireis', 'Brei'] == ([r.name for r in result])


class JSLintTest(zeit.cms.testing.JSLintTestCase):
    include = ('zeit.wochenmarkt.browser:resources',)
