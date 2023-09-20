import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    def test_inline_form_saves_values(self):
        self.get_article(with_block='citation')
        b = self.browser
        b.open('editable-body/blockname/@@edit-citation?show_form=1')
        b.getControl('Citation', index=0).value = 'fooooo'
        b.getControl('Attribution', index=0).value = 'John Doe'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual(
            'John Doe', b.getControl('Attribution', index=0).value)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_citation_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('citation')
        s.assertElementPresent('css=.block.type-citation .inline-form '
                               '.field.fieldname-text')
        s.assertElementPresent('css=.block.type-citation .inline-form '
                               '.field.fieldname-attribution')
