import gocept.testing.assertion
import zeit.cms.testing
import zeit.magazin.testing


class ZMOLinkCRUD(zeit.cms.testing.BrowserTestCase,
                  gocept.testing.assertion.String):

    layer = zeit.magazin.testing.LAYER

    def test_zmo_link_has_facebook_magazin_fields(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/magazin')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Link']
        b.open(menu.value[0])

        b.getControl('File name').value = 'link'
        b.getControl('Title').value = 'title'
        b.getControl('Ressort', index=0).displayValue = ['Leben']
        b.getControl('Teaser title').value = 'teaser'
        b.getControl('Link address').value = 'http://example.com'

        b.getControl('Facebook Magazin Text').value = 'mymagazin'
        b.getControl(name='form.actions.add').click()

        self.assertEndsWith('@@edit.html', b.url)
        self.assertEqual(
            'mymagazin', b.getControl('Facebook Magazin Text').value)

        b.getLink('Checkin').click()
        self.assertEllipsis('...mymagazin...', b.contents)
