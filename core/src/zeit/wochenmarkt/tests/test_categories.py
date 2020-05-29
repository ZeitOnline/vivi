# -*- coding: utf-8 -*-

import zope.component
import zeit.wochenmarkt.interfaces
import zeit.wochenmarkt.testing


class TestCategories(zeit.wochenmarkt.testing.FunctionalTestCase):
    """Testing ..ingredients.Categories"""

    def test_category_should_be_found_through_xml(self):
        categories = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist)._load()
        pizza = dict(categories.items()).get('pizza')
        assert 'Pizza' == pizza.name

    def test_category_should_be_found_by_id(self):
        bowl = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist).get('bowl')
        assert 'Bowl' == bowl.name

    def test_autocomplete_should_be_available_for_categrories(self):
        result = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist).search('B')
        assert 2 == len(result)
        names = []
        for item in result:
            names.append(item.name)
        assert u'Barbecue' in names
