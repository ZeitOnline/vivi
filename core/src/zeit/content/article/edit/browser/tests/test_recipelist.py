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
