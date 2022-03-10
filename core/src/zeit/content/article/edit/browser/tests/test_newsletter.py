import zeit.content.article.edit.browser.testing


class Newsletter(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'newslettersignup'

    def test_select_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl(label='Z+/Abonnenten').selected = True
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)  # XXX
        assert b.getControl(label='Z+/Abonnenten').selected
