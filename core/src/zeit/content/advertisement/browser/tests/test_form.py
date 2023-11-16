import zeit.content.advertisement.testing


class AdvertisementTest(zeit.content.advertisement.testing.BrowserTestCase):
    def test_advertisement_can_be_added(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Publisher advertisement']
        b.open(menu.value[0])

        b.getControl('File name').value = 'example'
        b.getControl('Title').value = 'My Ad'
        b.getControl('Link address').value = 'http://example.com'
        b.getControl(name='form.actions.add').click()
        self.assertNotIn('There were errors', b.contents)

        self.assertEqual('http://example.com', b.getControl('Link address').value)
