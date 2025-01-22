import pytest

import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    @pytest.mark.xfail()
    def test_inline_form_saves_default_values(self):
        self.get_article(with_block='tickaroo_liveblog')
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog-tickaroo?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Liveblog id').value)
        self.assertTrue(b.getControl('Collapse preceding content').selected)
        self.assertEqual(['(nothing selected)'], b.getControl(('Timeline Content')).displayValue)

    def test_inline_form_saves_values(self):
        self.get_article(with_block='tickaroo_liveblog')
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog-tickaroo?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl(('Timeline Content')).displayValue = ['Highlighted events']
        b.getControl('Collapse preceding content').selected = False
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Liveblog id').value)
        self.assertFalse(b.getControl('Collapse preceding content').selected)
        self.assertEqual(['Highlighted events'], b.getControl(('Timeline Content')).displayValue)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_liveblog_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('tickaroo_liveblog')
        s.assertElementPresent(
            'css=.block.type-tickaroo_liveblog .inline-form .field.fieldname-liveblog_id'
        )
        s.assertElementPresent(
            'css=.block.type-tickaroo_liveblog .inline-form '
            '.field.fieldname-collapse_preceding_content'
        )
