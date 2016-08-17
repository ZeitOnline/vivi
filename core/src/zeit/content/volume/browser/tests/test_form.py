import zeit.cms.testing
import zeit.content.volume.testing


class VolumeBrowserTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.volume.testing.ZCML_LAYER

    def open_add_form(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Volume']
        b.open(menu.value[0])

    def test_add_form_prefills_year_and_volume_from_global_settings(self):
        self.open_add_form()
        b = self.browser
        self.assertEqual('2008', b.getControl('Year').value)
        self.assertEqual('26', b.getControl('Volume').value)

    def test_automatically_sets_filename_using_year_and_volume(self):
        self.open_add_form()
        b = self.browser
        b.getControl('Year').value = '2010'
        b.getControl('Volume').value = '2'
        b.getControl('Add').click()
        self.assertEqual('http://localhost/++skin++vivi/repository/'
                         'ausgabe-2010-02/@@view.html', b.url)
