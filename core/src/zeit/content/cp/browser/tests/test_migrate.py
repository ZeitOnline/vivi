from zeit.cms.checkout.helper import checked_out
from zeit.content.cp.centerpage import CenterPage
from zeit.content.cp.interfaces import ICP2009, ICP2015
import zeit.cms.testing
import zeit.content.cp.testing
import zope.interface


class MigrateTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.cp.testing.layer

    def test_new_cp_provides_current_interface(self):
        self.repository['cp'] = CenterPage()
        with checked_out(self.repository['cp']):
            pass
        self.assertTrue(ICP2015.providedBy(self.repository['cp']))


class MigrateBrowserTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def setUp(self):
        super(MigrateBrowserTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['cp'] = CenterPage()
                with checked_out(self.repository['cp']) as cp:
                    zope.interface.noLongerProvides(cp, ICP2015)
                    zope.interface.alsoProvides(cp, ICP2009)
        self.browser.open(
            'http://localhost/++skin++vivi/repository/cp/@@checkout')

    def test_old_cp_show_warning_instead_of_editor(self):
        b = self.browser
        self.assertEllipsis('...Attention...change the type...', b.contents)

    def test_migrate_changes_interface(self):
        b = self.browser
        b.handleErrors = False
        b.getControl('Migrate').click()
        b.getLink('Edit', index=1).click()
        with self.assertRaises(LookupError):
            b.getControl('Migrate')
        b.getLink('Checkin').click()
        self.assertTrue(ICP2015.providedBy(self.repository['cp']))
