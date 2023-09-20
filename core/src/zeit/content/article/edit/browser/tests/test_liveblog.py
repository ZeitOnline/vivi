import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    def test_inline_form_saves_default_values(self):
        self.get_article(with_block='liveblog')
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Liveblog id').value)
        self.assertEqual(
            ['3'],
            b.getControl('Liveblog version').displayValue)
        self.assertTrue(b.getControl('Collapse preceding content').selected)

    def test_inline_form_saves_values_including_version(self):
        self.get_article(with_block='liveblog')
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Liveblog version').displayValue = ['3']
        b.getControl('Collapse preceding content').selected = False
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Liveblog id').value)
        self.assertEqual(['3'], b.getControl('Liveblog version').displayValue)
        self.assertFalse(b.getControl('Collapse preceding content').selected)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_liveblog_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('liveblog')
        s.assertElementPresent('css=.block.type-liveblog .inline-form '
                               '.field.fieldname-blog_id')
        s.assertElementPresent('css=.block.type-liveblog .inline-form '
                               '.field.fieldname-version')
        s.assertElementPresent('css=.block.type-liveblog .inline-form '
                               '.field.fieldname-collapse_preceding_content')
