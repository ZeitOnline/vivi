from datetime import datetime
import pytz
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zope.component.hooks


class TestAdminMenu(zeit.cms.testing.ZeitCmsBrowserTestCase):

    login_as = 'zmgr:mgrpw'

    def test_admin_menu_is_displayed_for_repository_objects(self):
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent')
        self.assertIn('Admin Menu', self.browser.contents)

    def test_admin_menu_co_is_hidden_for_repository_objects(self):
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent')
        self.assertNotIn('Admin CO', self.browser.contents)

    def test_admin_menu_is_hidden_for_checked_out_objects(self):
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink('Checkout').click()
        self.assertNotIn('Admin Menu', self.browser.contents)

    def test_admin_menu_co_is_displayed_for_checked_out_objects(self):
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink('Checkout').click()
        self.assertIn('Admin CO', self.browser.contents)

    def test_change_dates(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi'
               '/repository/testcontent/@@admin.html')
        b.getControl('Adjust last published').value = '2001-01-07 11:22:33'
        b.getControl('Adjust first released').value = '2001-01-08 11:22:33'
        b.getControl('Apply').click()
        zope.component.hooks.setSite(self.getRootFolder())
        content = self.repository['testcontent']
        publish = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertEqual(
            datetime(2001, 1, 7, 10, 22, 33, tzinfo=pytz.UTC),
            publish.date_last_published_semantic)
        self.assertEqual(
            datetime(2001, 1, 8, 10, 22, 33, tzinfo=pytz.UTC),
            publish.date_first_released)
