# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'audio'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-audio?show_form=1')
        b.getControl('Audio id').value = 'song'
        b.getControl('Apply').click()
        b.open('@@edit-audio?show_form=1')  # XXX
        self.assertEqual('song', b.getControl('Audio id').value)


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_audio_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('audio')
        s.assertElementPresent('css=.block.type-audio .inline-form '
                               '.field.fieldname-audio_id')


class AudioEditTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_audio_id_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('audio')
        # XXX a label-selector would be nice (gocept.selenium #6492)
        input = 'css=.block.type-audio form.wired input'
        s.waitForElementPresent(input)
        s.type(input, 'asdf')
        s.fireEvent(input, 'blur')
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(input)
        s.assertValue(input, 'asdf')
