import zeit.campus.testing


class ZCOLinkCRUD(zeit.cms.testing.BrowserTestCase):
    layer = zeit.campus.testing.WSGI_LAYER

    def test_zmo_link_has_facebook_campus_fields(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/campus')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Link']
        b.open(menu.value[0])

        b.getControl('File name').value = 'link'
        b.getControl(name='form.teaserTitle').value = 'title'
        b.getControl('Ressort', index=0).displayValue = ['Leben']
        b.getControl('Link address').value = 'http://example.com'
        b.getControl('Facebook Campus Text').value = 'mycampus'
        b.getControl(name='form.actions.add').click()

        self.assertEndsWith('@@edit.html', b.url)
        self.assertEqual('mycampus', b.getControl('Facebook Campus Text').value)

        b.getLink('Checkin').click()
        self.assertEllipsis('...mycampus...', b.contents)
