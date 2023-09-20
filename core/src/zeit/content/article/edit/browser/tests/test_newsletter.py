import zeit.content.article.edit.browser.testing


class Newsletter(zeit.content.article.edit.browser.testing.BrowserTestCase):

    def test_select_form_saves_values(self):
        self.get_article(with_block='newslettersignup')
        b = self.browser
        b.open('editable-body/blockname/@@edit-newslettersignup?show_form=1')
        b.getControl(label='Z+/Abonnenten').selected = True
        b.getControl('Apply').click()
        b.reload()
        assert b.getControl(label='Z+/Abonnenten').selected
