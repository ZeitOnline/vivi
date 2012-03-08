# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'video'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-video?show_form=1')
        b.getControl('Layout').displayValue = ['large']
        b.getControl('Apply').click()
        # Locate the layout widget by name here since we have several forms
        # with a "Layout" field so we couldn't be sure we have wired the
        # correct one just by looking at this one, common label.
        b.open('@@edit-video?show_form=1')
        layout = b.getControl(name='video.blockname.layout')
        self.assertEqual(['large'], layout.displayValue)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_video_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('video')
        s.assertElementPresent('css=.block.type-video .inline-form '
                               '.widget-outer.fieldname-layout')
