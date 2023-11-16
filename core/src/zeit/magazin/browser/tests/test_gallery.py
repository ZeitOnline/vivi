import zeit.magazin.testing


class ZMOGalleryCRUD(zeit.magazin.testing.BrowserTestCase):
    def test_zmo_gallery_has_facebook_magazin_fields(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/magazin')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Gallery']
        b.open(menu.value[0])

        b.getControl('File name').value = 'gallery'
        b.getControl('Title').value = 'title'
        b.getControl('Ressort', index=0).displayValue = ['Leben']
        b.getControl('Teaser title').value = 'teaser'
        b.getControl(name='form.image_folder').value = 'http://xml.zeit.de/online/2007/01'
        b.getControl(name='form.authors.0.').value = 'Author'

        b.getControl('Facebook Magazin Text').value = 'mymagazin'
        b.getControl(name='form.actions.add').click()

        self.assertEndsWith('@@overview.html', b.url)
        b.getLink('Edit metadata').click()
        self.assertEqual('mymagazin', b.getControl('Facebook Magazin Text').value)

        b.getLink('Checkin').click()
        self.assertEllipsis('...mymagazin...', b.contents)
