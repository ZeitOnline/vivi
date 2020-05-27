# -*- coding: utf-8 -*-
import zeit.content.article.edit.browser.testing


class RecipeListTest(
        zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'recipelist'

    def test_servings_should_be_validated(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)

        # Should accept a number
        b.getControl('Servings').value = 4
        b.getControl('Apply').click()
        self.assertNotEllipsis(
            '...Servings must be a positive number or empty...',
            b.contents)

        # Should accept an empty value
        b.open('@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Servings').value = ''
        b.getControl('Apply').click()
        self.assertNotEllipsis(
            '...Servings must be a positive number or empty...',
            b.contents)

        # Should NOT accept zero
        b.open('@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Servings').value = 0
        b.getControl('Apply').click()
        self.assertEllipsis(
            '...Servings must be a positive number or empty...',
            b.contents)

        # Should NOT accept a string
        b.open('@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Servings').value = 'notanumber'
        b.getControl('Apply').click()
        self.assertEllipsis(
            '...Servings must be a positive number or empty...',
            b.contents)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_recipelist_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('recipelist')
        s.assertElementPresent('css=.block.type-recipelist .inline-form '
                               '.field.fieldname-ingredients')

    def test_ingredients_should_be_organized_through_recipelist(self):
        s = self.selenium
        self.add_article()
        self.create_block('recipelist')
        s.waitForElementPresent('//input[@name="add_ingredient"]')

        # Add first ingredient
        s.type('//input[@name="add_ingredient"]', 'Brat')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')

        self.assertEqual(s.getCssCount('css=li.ingredient__item'), 1)
        s.assertText('css=a.ingredient__label', u'Brathähnchen')
        s.assertElementPresent('css=input.ingredient__amount')
        s.assertElementPresent('css=select.ingredient__unit')
        s.assertElementPresent('css=li.ingredient__item span.delete')

        # Add second ingredient
        s.type('//input[@name="add_ingredient"]', 'Nudel')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')
        self.assertEqual(s.getCssCount('css=li.ingredient__item'), 2)
        s.assertText(
            '//li[@class="ingredient__item"][1]/a[@class="ingredient__label"]',
            'Bandnudeln')

        # Duplicates should be prevented
        s.type('//input[@name="add_ingredient"]', 'Nudel')
        s.waitForVisible('css=ul.ui-autocomplete li')
        # XXX This is tricky, but we somehow need to lose focus on the whole
        # widget and blur does not work this time. Maybe there is another way?
        s.clickAt('css=ul.ui-autocomplete li', '-20,0')
        s.waitForVisible('css=li.ingredient__item')
        self.assertEqual(s.getCssCount('css=li.ingredient__item'), 2)  # not 3

        # Reorder ingredients
        s.dragAndDrop('css=li.ingredient__item', '0,50')
        s.waitForVisible('css=li.ingredient__item')
        s.assertText(
            '//li[@class="ingredient__item"][1]/a[@class="ingredient__label"]',
            'Brathähnchen')

        # Delete ingredient
        s.click('css=li.ingredient__item span.delete')
        self.assertEqual(s.getCssCount('css=li.ingredient__item'), 1)

    def test_ingredient_amount_should_be_validated(self):
        s = self.selenium
        self.add_article()
        self.create_block('recipelist')
        s.waitForElementPresent('//input[@name="add_ingredient"]')

        # Add ingredient
        s.type('//input[@name="add_ingredient"]', 'Brat')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')

        # Should accept numbers
        s.type('css=input.ingredient__amount', '2')
        # Lose focus to save new value
        s.runScript(
            'document.querySelector("input.ingredient__amount").blur()')
        # Give it some time to exchange widget with new value
        s.waitForVisible('css=input.ingredient__amount')
        s.assertAttribute('css=input.ingredient__amount@value', '2')

        # Should not accept letters
        s.type('css=input.ingredient__amount', 'oans')
        s.waitForVisible('css=input.ingredient__amount')  # Prevent flapping
        s.runScript(
            'document.querySelector("input.ingredient__amount").blur()')
        s.waitForVisible('css=input.ingredient__amount')
        # Fallback to previous value
        s.assertAttribute('css=input.ingredient__amount@value', '2')

        # Should accept empty value
        s.clear('css=input.ingredient__amount')
        s.waitForVisible('css=input.ingredient__amount')  # Prevent flapping
        s.runScript(
            'document.querySelector("input.ingredient__amount").blur()')
        s.waitForVisible('css=input.ingredient__amount')
        s.assertAttribute('css=input.ingredient__amount@value', '')

    def test_ingredient_should_store_values_as_json(self):
        s = self.selenium
        self.add_article()
        self.create_block('recipelist')
        s.waitForElementPresent('//input[@name="add_ingredient"]')

        # Add ingredient
        s.type('//input[@name="add_ingredient"]', 'Brat')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')

        s.type('css=input.ingredient__amount', '2')
        s.runScript(
            'document.querySelector("input.ingredient__amount").blur()')
        s.assertAttribute(
            'css=.ingredients-widget input@value',
            '[{"code":"brathaehnchen","label":"Brathähnchen",'
            '"amount":"2","unit":"Stück"}]')
