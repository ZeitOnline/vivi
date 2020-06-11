# -*- coding: utf-8 -*-
import zeit.content.article.edit.browser.testing


class RecipeCategoriesTest(
        zeit.content.article.edit.browser.testing.BrowserTestCase):

    def test_genre_should_toggle_recipe_categories(self):
        b = self.browser
        genre = b.getControl(name='metadata-genre.genre')
        # Select Leserartikel, which is an invalid recipe genre
        genre.value = 'dfb855684dc34acd36a91fa51bdce6ca'
        b.getControl(name='metadata-genre.actions.apply').click()
        b.open('@@contents')
        self.assertTrue(
            '<div class="recipe-categories-widget"' not in (b.contents))
        # We still expect an empty fieldset
        self.assertTrue(
            '<fieldset id="form-recipe-categories" /></form>' in (b.contents))

        genre = b.getControl(name='metadata-genre.genre')
        # Select Rezept, which is a valid recipe genre
        genre.value = 'ad481072a560c999a9044b43f26ced28'
        b.getControl(name='metadata-genre.actions.apply').click()
        b.open('@@contents')
        self.assertTrue('<div class="recipe-categories-widget"' in b.contents)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_recipe_categories_should_be_organizable(self):
        s = self.selenium
        self.add_article()
        s.click('css=#edit-form-metadata')
        s.waitForElementPresent('//input[@name="add_recipe_category"]')

        # Add first category
        s.type('//input[@name="add_recipe_category"]', 'Piz')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')

        self.assertEqual(s.getCssCount('css=li.recipe-category__item'), 1)
        s.assertText('css=a.recipe-category__label', u'Pizza')

        # Add second category
        s.type('//input[@name="add_recipe_category"]', 'Hüls')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')
        self.assertEqual(s.getCssCount('css=li.recipe-category__item'), 2)
        s.assertText(
            '//li[@class="recipe-category__item"][2]'
            '/a[@class="recipe-category__label"]',
            'Hülsenfrüchte')

        # Duplicates should be prevented
        s.type('//input[@name="add_recipe_category"]', 'Piz')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')
        # We need to trigger a save event to get rid of duplicates, but somehow
        # blur does not work in this test, so we just type enter instead...
        s.type('//input[@name="add_recipe_category"]', '\n')
        s.waitForCssCount('css=.busy', 0)
        self.assertEqual(
            s.getCssCount('css=li.recipe-category__item'), 2)  # not 3

        # Reorder ingredients
        s.dragAndDrop('css=li.recipe-category__item', '0,50')
        s.assertText(
            '//li[@class="recipe-category__item"][1]'
            '/a[@class="recipe-category__label"]',
            'Pizza')

        # Delete ingredient
        s.click('css=li.recipe-category__item span.delete')
        self.assertEqual(s.getCssCount('css=li.recipe-category__item'), 1)
