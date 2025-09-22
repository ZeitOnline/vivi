# -*- coding: utf-8 -*-

import zeit.wochenmarkt.testing


class TestIngredients(zeit.wochenmarkt.testing.FunctionalTestCase):
    """Testing ..ingredients.Ingredients"""

    def test_ingredient_should_be_found_through_xml(self):
        source = zeit.wochenmarkt.sources.ingredientsSource(None)
        basmati = source.find('basmatireis')
        assert 'Basmatireis' == basmati.name
        assert ['Reis', 'Basmati'] == basmati.qwords
        assert 'Basmatireis' == basmati.singular
        assert 'Basmatireis' == basmati.plural
        assert 'vegan' == basmati.diet

    def test_ingredient_should_be_found_by_id(self):
        source = zeit.wochenmarkt.sources.ingredientsSource(None)
        calamari = source.find('calamari')
        assert 'Calamari' == calamari.name
        assert ['Tintenfisch', 'Kalamar'] == calamari.qwords
        assert 'omnivore' == calamari.diet

    def test_autocomplete_should_be_available_for_ingredients(self):
        result = zeit.wochenmarkt.sources.ingredientsSource(None).factory.search('B')
        assert 8 == len(result)
        names = []
        for item in result:
            names.append(item.name)
        assert 'Brathähnchen' in names

    def test_ingredients_should_be_sorted_with_exact_match_leading(self):
        result = zeit.wochenmarkt.sources.ingredientsSource(None).factory.search('ei')
        assert ['Ei', 'Eis', 'Basmatireis', 'Brei'] == ([r.name for r in result])
