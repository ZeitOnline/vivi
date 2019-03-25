import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'topicbox'

    def test_topicbox_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.handleErrors = False
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('First').value = \
            'http://xml.zeit.de/online/2007/01/Somalia'
        b.getControl('Second').value = \
            'http://xml.zeit.de/online/2007/01/Somalia'
        b.getControl('Third').value = \
            'http://xml.zeit.de/online/2007/01/Somalia'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEqual('http://xml.zeit.de/online/2007/01/Somalia',
                         b.getControl('First').value)
        self.assertEqual('http://xml.zeit.de/online/2007/01/Somalia',
                         b.getControl('Second').value)
        self.assertEqual('http://xml.zeit.de/online/2007/01/Somalia',
                         b.getControl('Third').value)
