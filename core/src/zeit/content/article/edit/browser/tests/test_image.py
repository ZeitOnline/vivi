# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'image'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-image?show_form=1')
        b.getControl('Custom image sub text').value = 'foo bar'
        b.getControl('Apply').click()
        b.open('@@edit-image?show_form=1')  # XXX
        self.assertEqual(
            'foo bar', b.getControl('Custom image sub text').value)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_image_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('image')
        s.assertElementPresent('css=.block.type-image .inline-form '
                               '.field.fieldname-custom_caption')
        s.assertElementPresent('css=.block.type-image .inline-form '
                               '.field.fieldname-layout')
