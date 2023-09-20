import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'cardstack'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-cardstack?show_form=1')
        b.getControl('Cardstack id').value = 'bloggy'
        b.getControl('Advertorial?').click()
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Cardstack id').value)
        self.assertEqual(True, b.getControl('Advertorial?').selected)
