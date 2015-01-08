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
