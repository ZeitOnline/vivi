from zeit.content.image.browser.tests.test_imagegroup import ImageGroupHelperMixin
import zeit.content.image.mdb
import zeit.content.image.testing
import zope.component


class MDBImportJavascript(zeit.content.image.testing.SeleniumTestCase):
    def setUp(self):
        super().setUp()
        zope.component.getGlobalSiteManager().registerUtility(zeit.content.image.mdb.FakeMDB())

    def test_prefills_form_fields(self):
        s = self.selenium
        s.open('/repository/@@zeit.content.image.imagegroup.Add')
        self.execute('document.getElementById("form.mdb_blob").widget.retrieve("4711")')
        s.waitForValue('name=form.caption', 'Testbilder Honorar')
        s.assertValue('name=form.copyright.combination_02', 'Peter Schwalbach')
        s.assertValue('name=form.mdb_id', '4711')
        s.assertValue('name=form.mdb_blob', '4711')
        s.assertValue('name=form.release_period.combination_01', '2019-01-01T*')


class MDBImport(zeit.content.image.testing.BrowserTestCase, ImageGroupHelperMixin):
    def setUp(self):
        super().setUp()
        zope.component.getGlobalSiteManager().registerUtility(zeit.content.image.mdb.FakeMDB())

    def test_downloads_image_data(self):
        self.add_imagegroup()
        self.browser.getControl(name='form.mdb_id').value = '4711'
        self.browser.getControl(name='form.mdb_blob').value = '4711'
        self.save_imagegroup()
        group = self.repository['imagegroup']
        image = group.master_image_for_viewport('desktop')
        self.assertEqual((119, 160), image.getImageSize())
