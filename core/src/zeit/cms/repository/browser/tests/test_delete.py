import urllib.error

from zope.testbrowser.browser import LinkNotFoundError

from zeit.cms import testing
from zeit.cms.repository.folder import Folder
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS, IPublish, IPublishInfo


class TestDelete(testing.ZeitCmsBrowserTestCase):
    def test_delete_menu_item_is_displayed_for_unpublished_objects(self):
        content = self.repository['testcontent']
        self.assertFalse(IPublishInfo(content).published)
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink(url='@@delete.html')  # assert link exists

    def test_delete_menu_item_is_not_displayed_for_published_objects(self):
        content = self.repository['testcontent']
        IPublishInfo(content).set_can_publish(CAN_PUBLISH_SUCCESS)
        IPublish(content).publish()
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        with self.assertRaises(LinkNotFoundError):
            self.browser.getLink(url='@@delete.html')

    def test_delete_button_is_displayed_for_folder_without_published_objects(self):
        folder = self.repository['testing']
        folder['foo'] = ExampleContentType()
        self.assertFalse(IPublishInfo(folder).published)
        browser = testing.Browser(self.layer['wsgi_app'])
        browser.login('producer', 'producerpw')
        browser.open('http://localhost:8080/++skin++vivi/repository/testing')
        link = browser.getLink(url='@@delete.html')
        url = link.url.split("'")[1]  # embedded in lightbox javascript
        browser.open(url)
        browser.getControl('Delete')  # 'Delete' button exists

    def test_delete_button_is_not_displayed_for_folder_with_published_objects(self):
        folder = self.repository['testing']
        folder['foo'] = content = ExampleContentType()
        self.assertFalse(IPublishInfo(folder).published)
        IPublishInfo(content).set_can_publish(CAN_PUBLISH_SUCCESS)
        IPublish(content).publish()
        browser = testing.Browser(self.layer['wsgi_app'])
        browser.login('producer', 'producerpw')
        browser.open('http://localhost:8080/++skin++vivi/repository/testing')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink(url='@@delete.html')
        browser.open('@@delete.html')
        with self.assertRaises(LookupError):
            browser.getControl('Delete')  # 'Delete' button is missing

    def test_delete_button_is_not_displayed_for_folder_with_subfolder(self):
        folder = self.repository['online']
        subfolder = folder['2005']
        self.assertFalse(IPublishInfo(folder).published)
        self.assertFalse(IPublishInfo(subfolder).published)
        browser = testing.Browser(self.layer['wsgi_app'])
        browser.login('producer', 'producerpw')
        browser.open('http://localhost:8080/++skin++vivi/repository/online')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink(url='@@delete.html')
        browser.open('@@delete.html')
        with self.assertRaises(LookupError):
            browser.getControl('Delete')  # 'Delete' button is missing

    def test_delete_folder_is_not_allowed_for_normal_user(self):
        self.repository['folder'] = Folder()
        b = self.browser
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open('/repository/folder/@@delete.html')
            self.assertEqual(403, info.exception.status)

    def test_delete_folder_success(self):
        self.repository['folder'] = Folder()
        self.repository['folder']['foo'] = ExampleContentType()
        b = testing.Browser(self.layer['wsgi_app'])
        b.login('producer', 'producerpw')
        b.open('/repository/folder/@@delete.html')
        self.assertEllipsis('...Do you really want to delete the object...', b.contents)
        b.getControl('Delete').click()
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open('/repository/folder')
            self.assertEqual(404, info.exception.status)

    def delete_content_success(self):
        b = self.browser
        b.open('/testcontent/@@delete.html')
        self.assertEllipsis('...Do you really want to delete the object...', b.contents)
        b.getControl('Delete').click()
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open('/repository/testcontent')
            self.assertEqual(404, info.exception.status)
        b.open('/repository')
        self.assertNotEllipsis('...testcontent...', b.contents)
