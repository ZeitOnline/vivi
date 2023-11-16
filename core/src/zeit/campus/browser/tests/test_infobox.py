import zeit.campus.testing


class ZCOInfoboxDebate(zeit.campus.testing.BrowserTestCase):
    def test_zco_infobox_has_debate_field(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/campus')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Infobox']
        b.open(menu.value[0])

        b.getControl('File name').value = 'info'
        b.getControl('Supertitle').value = 'spitz'
        b.getControl('Debate action URL').value = 'mailto:foo@example.com'
        b.getControl(name='form.actions.add').click()

        self.assertEndsWith('@@edit.html', b.url)
        self.assertEqual('mailto:foo@example.com', b.getControl('Debate action URL').value)

        b.getLink('Checkin').click()
        self.assertEllipsis('...mailto:foo@example.com...', b.contents)
