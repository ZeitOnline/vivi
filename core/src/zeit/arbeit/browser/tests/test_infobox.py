import zeit.cms.testing
import zeit.arbeit.testing


class ZARInfoboxDebateTest(zeit.arbeit.testing.BrowserTestCase):
    def test_zar_infobox_has_debate_field(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/arbeit')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Infobox']
        b.open(menu.value[0])

        b.getControl('File name').value = 'info'
        b.getControl('Supertitle').value = 'spitz'
        # Has to be set, so Vivi adds the section marker
        b.getControl('Ressort').displayValue = ['Arbeit']
        b.getControl(name='form.actions.add').click()
        # Now the Debate field is available
        b.getControl('Debate action URL').value = 'mailto:foo@example.com'
        b.getControl(name='form.actions.apply').click()
        self.assertEndsWith('@@edit.html', b.url)
        self.assertEqual('mailto:foo@example.com', b.getControl('Debate action URL').value)
        b.getLink('Checkin').click()
        self.assertEllipsis('...mailto:foo@example.com...', b.contents)
