import zeit.magazin.testing


class ZMOPortraitboxCRUD(zeit.magazin.testing.BrowserTestCase):
    def test_zmo_portraitbox_has_longtext_field(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/magazin')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Portraitbox']
        b.open(menu.value[0])

        b.getControl('File name').value = 'portrait'
        b.getControl('First and last name').value = 'Foo Bar'
        b.getControl('Text').value = '<p><strong>With</strong> markup</p>'
        b.getControl('long text (ZMO)').value = '<p><strong>Second</strong> text</p>'
        b.getControl('Add').click()

        self.assertEndsWith('@@edit.html', b.url)
        self.assertEqual(
            '<p><strong>Second</strong> text</p>', b.getControl('long text (ZMO)').value.strip()
        )

        b.getLink('Checkin').click()
        self.assertEllipsis('...&lt;strong&gt;Second&lt;/strong&gt; text...', b.contents)
