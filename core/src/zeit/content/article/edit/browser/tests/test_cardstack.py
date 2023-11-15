import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_inline_form_saves_values(self):
        self.get_article(with_block='cardstack')
        b = self.browser
        b.open('editable-body/blockname/@@edit-cardstack?show_form=1')
        b.getControl('Cardstack id').value = 'bloggy'
        b.getControl('Advertorial?').click()
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Cardstack id').value)
        self.assertEqual(True, b.getControl('Advertorial?').selected)
