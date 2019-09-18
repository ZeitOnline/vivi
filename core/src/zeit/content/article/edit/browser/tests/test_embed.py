import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'embed'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Embed URL').value = 'https://twitter.com/foo/status/123'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)  # XXX
        self.assertEqual(
            'https://twitter.com/foo/status/123',
            b.getControl('Embed URL').value)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_embed_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('embed')
        s.assertElementPresent('css=.block.type-embed .inline-form '
                               '.field.fieldname-url')
