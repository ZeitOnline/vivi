# -*- coding: utf-8 -*-
import lxml.etree
import zope.component

import zeit.content.article.article
import zeit.wochenmarkt.interfaces
import zeit.wochenmarkt.testing


class TestRecipeCategoriesWhitelist(zeit.wochenmarkt.testing.FunctionalTestCase):
    def test_category_should_be_found_through_xml(self):
        categories = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist
        )._load()
        pizza = dict(categories.items()).get('pizza')
        assert 'Pizza' == pizza.name

    def test_category_should_be_found_by_id(self):
        bowl = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist
        ).get('bowl')
        assert 'Bowl' == bowl.name

    def test_autocomplete_should_be_available_for_categrories(self):
        result = zope.component.getUtility(
            zeit.wochenmarkt.interfaces.IRecipeCategoriesWhitelist
        ).search('B')
        assert 2 == len(result)
        names = []
        for item in result:
            names.append(item.name)
        assert 'Barbecue' in names


class TestRecipeCategories(
    zeit.wochenmarkt.testing.FunctionalTestCase, zeit.wochenmarkt.testing.RecipeCategoriesHelper
):
    def get_content(self):
        from lxml import objectify

        from zeit.wochenmarkt.categories import RecipeCategories

        class Content:
            categories = RecipeCategories()
            xml = objectify.fromstring('<article><head/></article>')

        return Content()

    def test_set_should_add_new_categories(self):
        categories = self.setup_categories('summer', 'pizza')
        summer = categories['summer']
        pizza = categories['pizza']
        content = self.get_content()
        content.categories = [summer, pizza]
        result = content.categories
        self.assertEqual(['summer', 'pizza'], [x.code for x in result])

    def test_set_should_add_duplicate_values_only_once(self):
        categories = self.setup_categories('summer')
        summer = categories['summer']
        content = self.get_content()
        content.categories = [summer, summer]
        result = content.categories
        self.assertEqual(['summer'], [x.code for x in result])

    def test_set_should_write_categories_to_xml_head(self):
        categories = self.setup_categories('summer')
        summer = categories['summer']
        content = self.get_content()
        content.categories = [summer]
        self.assertEllipsis(
            '<recipe_categories...><category code="summer"/>...',
            lxml.etree.tostring(content.xml.head.recipe_categories, encoding=str),
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
