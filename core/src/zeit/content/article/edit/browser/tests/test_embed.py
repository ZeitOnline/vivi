import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_inline_form_saves_values(self):
        self.get_article(with_block='embed')
        b = self.browser
        b.open('editable-body/blockname/@@edit-embed?show_form=1')
        b.getControl('Embed URL').value = 'https://twitter.com/foo/status/123'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('https://twitter.com/foo/status/123', b.getControl('Embed URL').value)

    def test_domain_must_be_included_in_supported_list(self):
        self.get_article(with_block='embed')
        b = self.browser
        b.open('editable-body/blockname/@@edit-embed?show_form=1')
        b.getControl('Embed URL').value = 'http://invalid.com/'
        b.getControl('Apply').click()
        self.assertEllipsis('...Unsupported embed domain...', b.contents)

    def test_shows_manual_link(self):
        self.get_article(with_block='embed')
        b = self.browser
        b.open('editable-body/blockname/@@edit-embed?show_form=1')
        b.reload()
        self.assertEllipsis('...href="http://example.com/embed">Manual-Link</a>...', b.contents)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_embed_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('embed')
        s.assertElementPresent('css=.block.type-embed .inline-form ' '.field.fieldname-url')
