from subprocess import check_output
import unittest

import zeit.content.article.edit.browser.testing
import zeit.content.image.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_inline_form_saves_values_for_box(self):
        group = zeit.content.image.testing.create_image_group()
        self.get_article(with_block='box')
        b = self.browser
        b.open('editable-body/blockname/@@edit-box?show_form=1')
        b.getControl(name='form.supertitle').value = 'super'
        b.getControl(name='form.title').value = 'title'
        b.getControl(name='form.subtitle').value = 'text'
        b.getControl(name='form.image').value = group.uniqueId
        b.getControl(name='form.layout').displayValue = ['News-Artikel Tabelle']
        b.getControl('Apply').click()
        b.reload()
        self.assertEllipsis('text', b.getControl(name='form.subtitle').value)
        self.assertEqual('title', b.getControl(name='form.title').value)
        self.assertEqual('super', b.getControl(name='form.supertitle').value)
        self.assertEqual(['News-Artikel Tabelle'], b.getControl(name='form.layout').displayValue)
        self.assertEqual(group.uniqueId, b.getControl(name='form.image').value)

    @unittest.skipUnless(
        check_output('pandoc --version', shell=True).startswith(b'pandoc 1'), 'pandoc not available'
    )
    def test_teaser_text_field_markdown_is_stored_correctly(self):
        self.get_article(with_block='box')
        b = self.browser
        b.open('editable-body/blockname/@@edit-box?show_form=1')
        b.getControl(name='form.subtitle').value = '#h1 text'
        b.getControl('Apply').click()
        b.reload()
        self.assertEllipsis('# h1 text', b.getControl(name='form.subtitle').value)
