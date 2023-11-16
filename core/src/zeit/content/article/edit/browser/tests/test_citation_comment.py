import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_inline_form_saves_values(self):
        self.get_article(with_block='citation_comment')
        b = self.browser
        b.open('editable-body/blockname/@@edit-citation-comment?show_form=1')
        b.getControl('Citation Comment', index=0).value = 'Der beste Kommentar'
        b.getControl('URL', index=0).value = 'http://foo.de'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('http://foo.de', b.getControl('URL', index=0).value)
        self.assertEqual('Der beste Kommentar', b.getControl('Citation Comment', index=0).value)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_citation_comment_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('citation_comment')
        s.assertElementPresent(
            'css=.block.type-citation_comment .inline-form ' '.field.fieldname-text'
        )
        s.assertElementPresent(
            'css=.block.type-citation_comment .inline-form '
            '.field.fieldname-url '
            'input[data-comments-api-url='
            '"https://comments.staging.zeit.de"]'
        )
