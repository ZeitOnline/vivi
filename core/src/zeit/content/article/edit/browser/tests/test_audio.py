import zeit.content.article.edit.browser.testing
import zeit.content.audio.audio


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'audio'

    def test_inline_form_saves_values(self):
        audio = zeit.content.audio.audio.Audio()
        audio.title = 'My Audio'
        audio = self.repository['audio'] = audio
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl(name='EditAudio.blockname.references').value = audio.uniqueId
        b.getControl('Apply').click()
        b.reload()
        self.assertEllipsis('...%s...' % audio.uniqueId, b.contents)
