import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'mail'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-mail?show_form=1')
        b.getControl('Recipient').value = 'test@localhost'
        b.getControl('Subject').displayValue = ['Apps']
        b.getControl('Success message').value = 'thankyou'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('test@localhost', b.getControl('Recipient').value)
        self.assertEqual(['Apps'], b.getControl('Subject').displayValue)
        self.assertEqual('thankyou', b.getControl('Success message').value)
