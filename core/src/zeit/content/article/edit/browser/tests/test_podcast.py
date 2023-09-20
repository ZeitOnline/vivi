import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'podcast'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-podcast?show_form=1')
        b.getControl('Podcast id').value = 'bloggy'
        b.getControl('Provider').displayValue = ['Tempus Corporate']
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Podcast id').value)
        self.assertEqual(
            ['Tempus Corporate'], b.getControl('Provider').displayValue)
