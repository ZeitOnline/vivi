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

    smoke = [
        ('one\n\ntwo\n\n', '<p>one</p>\n<p>two</p>'),
        (
            '* one\n* [two](https://example.com/)\n',
            '<ul>\n<li>one</li>\n<li><a href="https://example.com/">two</a></li>\n</ul>',
        ),
    ]

    def test_markdown_content_smoke(self):
        self.test_add_markup()
        b = self.browser
        for md, html in self.smoke:
            b.open('http://localhost/repository/online/2007/01/test-markdown/@@checkout')
            b.getControl('Markdown content').value = md
            b.getControl('Apply').click()
            self.assertNotIn('There were errors', b.contents)
            b.getLink('Checkin').click()
            self.assertEllipsis(f'...{html}...', b.contents)
