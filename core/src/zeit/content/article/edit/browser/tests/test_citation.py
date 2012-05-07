# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'citation'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-citation?show_form=1')
        b.getControl('Citation', index=0).value = 'fooooo'
        b.getControl('Attribution', index=0).value = 'John Doe'
        b.getControl('Apply').click()
        b.open('@@edit-citation?show_form=1')  # XXX
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
                               '.field.fieldname-attribution_2')
