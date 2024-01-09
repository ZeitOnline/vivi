# -*- coding: utf-8 -*-
import json

import zeit.content.article.edit.browser.testing


class RecipeListTest(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_servings_should_be_validated(self):
        self.get_article(with_block='recipelist')
        b = self.browser
        b.open('editable-body/blockname/@@edit-recipelist?show_form=1')

        # Should accept a number
        b.getControl('Servings').value = 4
        b.getControl('Apply').click()
        self.assertNotEllipsis('...<span class="error">...', b.contents)

        # Should accept an empty value
        b.reload()
        b.getControl('Servings').value = ''
        b.getControl('Apply').click()
        self.assertNotEllipsis('...<span class="error">...', b.contents)

        # Should NOT accept zero
        b.reload()
        b.getControl('Servings').value = 0
        b.getControl('Apply').click()
        self.assertEllipsis('...Value must be number or range...', b.contents)

        # Should NOT accept a string
        b.reload()
        b.getControl('Servings').value = 'notanumber'
        b.getControl('Apply').click()
        self.assertEllipsis('...Value must be number or range...', b.contents)


class FormLoader(
    zeit.content.article.edit.browser.testing.EditorTestCase,
    zeit.content.article.edit.browser.testing.RecipeListHelper,
):
    def test_recipelist_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('recipelist')
        s.assertElementPresent(
            'css=.block.type-recipelist .inline-form ' '.field.fieldname-ingredients'
        )

    def test_ingredients_should_be_organized_through_recipelist(self):
        s = self.selenium
        self.setup_ingredient()

        self.assertEqual(s.getCssCount('css=li.ingredient__item'), 1)
        s.assertText('css=a.ingredient__label', 'Brathähnchen')
        s.assertElementPresent('css=input.ingredient__amount')
        s.assertElementPresent('css=select.ingredient__unit')
        s.assertElementPresent('css=li.ingredient__item span.delete')

        # Add second ingredient
        s.type('//input[@name="add_ingredient"]', 'Nudel')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')
        self.assertEqual(s.getCssCount('css=li.ingredient__item'), 2)
        s.assertText(
            '//li[@class="ingredient__item"][2]/a[@class="ingredient__label"]', 'Bandnudeln'
        )

        # Reorder ingredients
        s.dragAndDrop('css=.ingredient__label', '0,50')
        s.waitForVisible('css=li.ingredient__item')
        s.assertText(
            '//li[@class="ingredient__item"][2]/a[@class="ingredient__label"]', 'Brathähnchen'
        )

        # Delete ingredient
        s.click('css=li.ingredient__item span.delete')
        self.assertEqual(s.getCssCount('css=li.ingredient__item'), 1)

    def test_ingredient_amount_should_be_validated(self):
        s = self.selenium
        self.setup_ingredient()

        # Should accept numbers
        s.type('css=input.ingredient__amount', '2')
        # Lose focus to save new value
        s.runScript('document.querySelector("input.ingredient__amount").blur()')
        # Give it some time to exchange widget with new value
        s.waitForCssCount('css=.dirty', 0)
        s.assertAttribute('css=input.ingredient__amount@value', '2')

        # Should not accept letters
        s.type('css=input.ingredient__amount', 'oans')
        s.runScript('document.querySelector("input.ingredient__amount").blur()')
        s.waitForCssCount('css=.dirty', 0)
        # Fallback to previous value
        s.assertAttribute('css=input.ingredient__amount@value', '2')

        # Should accept empty value
        s.clear('css=input.ingredient__amount')
        s.runScript('document.querySelector("input.ingredient__amount").blur()')
        s.waitForCssCount('css=.dirty', 0)
        s.assertAttribute('css=input.ingredient__amount@value', '')

    def test_ingredient_should_store_values_as_json(self):
        s = self.selenium
        self.setup_ingredient()

        s.type('css=input.ingredient__amount', '2')
        s.runScript('document.querySelector("input.ingredient__amount").blur()')
        s.waitForCssCount('css=.dirty', 0)
        ingredient_data = json.loads(s.getAttribute('css=.ingredients-widget input@value'))[0]
        assert ingredient_data.get('code') == 'brathaehnchen'
        assert ingredient_data.get('label') == 'Brathähnchen'
        assert ingredient_data.get('amount') == '2'
        assert ingredient_data.get('unit') == ''
        assert ingredient_data.get('details') == ''
        assert ingredient_data.get('unique_id') is not None

    def test_duplicate_ingredients_should_be_allowed(self):
        s = self.selenium
        self.add_article()
        self.create_block('recipelist')

        # Add first ingredient
        s.type('//input[@name="add_ingredient"]', 'Nudel')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')

        # Add duplicate ingredient
        s.type('//input[@name="add_ingredient"]', 'Nudel')
        s.waitForVisible('css=ul.ui-autocomplete li')
        s.click('css=ul.ui-autocomplete li')
        self.assertEqual(s.getCssCount('css=li.ingredient__item'), 2)

        # ids should be different.
        uid1 = s.getAttribute('//li[@class="ingredient__item"][1] @data-id')
        uid2 = s.getAttribute('//li[@class="ingredient__item"][2] @data-id')
        assert uid1 != uid2

    def test_ingredient_units_should_be_fetched_from_endpoint(self):
        s = self.selenium
        self.setup_ingredient()

        s.click('css=.ingredient__unit')
        s.click('//option[text()="Stück"]')
        s.clickAt('css=.ingredient__unit', '0,40')
        s.waitForCssCount('css=.dirty', 0)

        # Stored in html element
        s.assertValue('css=.ingredient__unit', 'stueck')

        # Check if all units are available for selection
        s.assertCssCount('css=.ingredient__unit option', 3)

        # Stored in JSON
        ingredient_data = json.loads(s.getAttribute('css=.ingredients-widget input@value'))[0]
        assert ingredient_data.get('code') == 'brathaehnchen'
        assert ingredient_data.get('unit') == 'stueck'

    def test_unset_recipe_title_should_print_hint(self):
        s = self.selenium
        self.add_article()
        self.create_block('recipelist')

        # Accessing pseudo elements in selenium is slightly annoying...
        title_content = (
            'window.getComputedStyle(document.querySelector('
            '".type-recipelist .fieldname-title"), ":before"'
            ').getPropertyValue("content")'
        )

        title_field = '.type-recipelist .fieldname-title input'

        # Show notification if no title has been set
        assert 'Bitte trag einen Rezeptnamen' in s.getEval(title_content)

        # After setting the title, the notification should disappear
        s.type('css=' + title_field, 'bananabread')
        s.runScript('document.querySelector("' + title_field + '").blur()')
        s.waitForCssCount('css=.dirty', 0)
        assert '"none"' == s.getEval(title_content)
