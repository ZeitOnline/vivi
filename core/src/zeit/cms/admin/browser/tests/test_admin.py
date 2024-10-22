from pendulum import datetime
import zope.component.hooks

import zeit.cms.testing
import zeit.cms.workflow.interfaces


class TestAdminMenu(zeit.cms.testing.ZeitCmsBrowserTestCase):
    login_as = 'zmgr:mgrpw'

    def test_admin_menu_is_displayed_for_repository_objects(self):
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        self.assertIn('Admin Menu', self.browser.contents)

    def test_admin_menu_co_is_hidden_for_repository_objects(self):
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        self.assertNotIn('Admin CO', self.browser.contents)

    def test_admin_menu_is_hidden_for_checked_out_objects(self):
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink('Checkout').click()
        self.assertNotIn('Admin Menu', self.browser.contents)

    def test_admin_menu_co_is_displayed_for_checked_out_objects(self):
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink('Checkout').click()
        self.assertIn('Admin CO', self.browser.contents)

    def test_change_dates(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi' '/repository/testcontent/@@admin.html')
        b.getControl('Adjust last published').value = '2001-01-07 11:22:33'
        b.getControl('Adjust first released').value = '2001-01-08 11:22:33'
        b.getControl('Apply').click()
        zope.component.hooks.setSite(self.getRootFolder())
        content = self.repository['testcontent']
        publish = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertEqual(datetime(2001, 1, 7, 10, 22, 33), publish.date_last_published_semantic)
        self.assertEqual(datetime(2001, 1, 8, 10, 22, 33), publish.date_first_released)

    def test_admin_menu_co_has_caching_time_field(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi' '/repository/testcontent')
        b.getLink('Checkout').click()
        b.getLink('Admin').click()
        b.getControl('Caching time browser').value = 0
        b.getControl('Caching time server').value = 60
        b.getControl('Apply').click()
        b.getLink('Checkin').click()
        zope.component.hooks.setSite(self.getRootFolder())
        content = self.repository['testcontent']
        caching_time = zeit.cms.content.interfaces.ICachingTime(content)
        self.assertEqual(0, caching_time.browser)
        self.assertEqual(60, caching_time.server)
