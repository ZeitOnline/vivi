import zeit.content.image.mdb
import zeit.content.image.testing
import zope.component


class MDBImport(zeit.content.image.testing.SeleniumTestCase):

    def setUp(self):
        super(MDBImport, self).setUp()
        zope.component.getGlobalSiteManager().registerUtility(
            zeit.content.image.mdb.FakeMDB())

    def test_prefills_form_fields(self):
        s = self.selenium
        s.open('/repository/@@zeit.content.image.imagegroup.Add')
        self.eval(
            'document.getElementById("form.mdb_blob").widget.retrieve("4711")')
        s.waitForValue('name=form.caption', 'Testbilder Honorar')
        s.assertValue('name=form.copyright.combination_02', 'Peter Schwalbach')
        s.assertValue('name=form.mdb_id', '4711')
        s.assertValue('name=form.mdb_blob', '4711')
