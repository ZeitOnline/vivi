import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'puzzleform'

    def test_puzzle_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.handleErrors = False
        b.open(
            'editable-body/blockname/@@edit-%s?show_form=1' % self.block_type)
        b.getControl('Puzzle').displayValue = ['Scrabble']
        b.getControl('Year').value = '2099'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)  # XXX
        self.assertEqual(['Scrabble'], b.getControl('Puzzle').displayValue)
        self.assertEqual('2099', b.getControl('Year').value)
