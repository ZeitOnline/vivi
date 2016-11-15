from mechanize import LinkNotFoundError
from z3c.etestbrowser.testing import ExtendedTestBrowser
from zeit.cms import testing
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublishInfo, IPublish
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS


class TestDeleteMenuItem(testing.ZeitCmsBrowserTestCase):

    def test_delete_menu_item_is_displayed_for_unpublished_objects(self):
        content = self.repository['testcontent']
        self.assertFalse(IPublishInfo(content).published)
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink(url='@@delete.html')   # assert link exists

    def test_delete_menu_item_is_not_displayed_for_published_objects(self):
        content = self.repository['testcontent']
        IPublishInfo(content).set_can_publish(CAN_PUBLISH_SUCCESS)
        IPublish(content).publish()
        self.browser.open(
            'http://localhost:8080/++skin++vivi/repository/testcontent')
        with self.assertRaises(LinkNotFoundError):
            self.browser.getLink(url='@@delete.html')

    def test_delete_menu_item_is_displayed_for_folder_without_published_objects(self):
        folder = self.repository['testing']
        self.assertFalse(IPublishInfo(folder).published)
        with testing.site(self.getRootFolder()):
            folder['foo'] = ExampleContentType()
        browser = ExtendedTestBrowser()
        browser.addHeader('Authorization', 'Basic producer:producerpw')
        browser.open(
            'http://localhost:8080/++skin++vivi/repository/testing')
        browser.getLink(url='@@delete.html')

    def test_delete_menu_item_is_not_displayed_for_folder_with_published_objects(self):
        folder = self.repository['testing']
        self.assertFalse(IPublishInfo(folder).published)
        with testing.site(self.getRootFolder()):
            folder['foo'] = content = ExampleContentType()
        IPublishInfo(content).set_can_publish(CAN_PUBLISH_SUCCESS)
        IPublish(content).publish()
        browser = ExtendedTestBrowser()
        browser.addHeader('Authorization', 'Basic producer:producerpw')
        browser.open(
            'http://localhost:8080/++skin++vivi/repository/testing')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink(url='@@delete.html')

    def test_delete_menu_item_is_not_displayed_for_folder_with_subfolder(self):
        folder = self.repository['online']
        self.assertFalse(IPublishInfo(folder).published)
        with testing.site(self.getRootFolder()):
            subfolder = folder['2005']
        self.assertFalse(IPublishInfo(subfolder).published)
        browser = ExtendedTestBrowser()
        browser.addHeader('Authorization', 'Basic producer:producerpw')
        browser.open(
            'http://localhost:8080/++skin++vivi/repository/online')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink(url='@@delete.html')
