import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'liveblog'

    def test_inline_form_saves_values_without_version(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)  # XXX
        self.assertEqual('bloggy', b.getControl('Liveblog id').value)
        self.assertEqual(
            ['(nothing selected)'],
            b.getControl('Liveblog version').displayValue)

    def test_inline_form_saves_values_including_version(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Liveblog version').displayValue = ['3']
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('bloggy', b.getControl('Liveblog id').value)
        self.assertIn('3', b.getControl('Liveblog version').displayValue)
