import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_puzzle_inline_form_saves_values(self):
        self.get_article(with_block='puzzleform')
        b = self.browser
        b.open('editable-body/blockname/@@edit-puzzleform?show_form=1')
        b.getControl('Puzzle').displayValue = ['Scrabble']
        b.getControl('Year').value = '2099'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual(['Scrabble'], b.getControl('Puzzle').displayValue)
        self.assertEqual('2099', b.getControl('Year').value)
