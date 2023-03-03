import zeit.content.markup.testing


class MarkupTest(zeit.content.markup.testing.BrowserTestCase):

    def test_add_markup(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/online/2007/01/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Markup']
        b.open(menu.value[0])

        b.getControl('Title').value = 'goodbye'
        b.getControl('Markdown content').value = '# sad noises'
        b.getControl('File name').value = 'test-markdown'

        b.getControl('Add').click()
        self.assertNotIn('There were errors', b.contents)
        b.getLink('Checkin').click()

        self.assertEllipsis('...goodbye...', b.contents)
        self.assertEllipsis('...<h1>sad noises</h1>...', b.contents)
