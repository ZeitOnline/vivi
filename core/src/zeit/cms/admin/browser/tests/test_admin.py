import zeit.cms.testing
import zope.testbrowser.testing


class TestAdminMenu(zeit.cms.testing.ZeitCmsBrowserTestCase):

    def setUp(self):
        super(TestAdminMenu, self).setUp()
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic zmgr:mgrpw')

    def test_admin_menu_is_displayed_for_repository_objects(self):
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent')
        self.assertIn('Admin Menu', self.browser.contents)

    def test_admin_menu_is_hidden_for_checked_out_objects(self):
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink('Checkout').click()
        self.assertNotIn('Admin Menu', self.browser.contents)
