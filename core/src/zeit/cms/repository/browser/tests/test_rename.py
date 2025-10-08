# coding: utf-8
import urllib.error

from zope.testbrowser.browser import LinkNotFoundError

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS, IPublish, IPublishInfo
import zeit.cms.testing


class TestRename(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_rename_menu_item_is_displayed_for_unpublished_objects(self):
        content = self.repository['testcontent']
        self.assertFalse(IPublishInfo(content).published)
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink(url='@@rename-box')  # assert link exists

    def test_rename_menu_item_is_not_displayed_for_published_objects(self):
        content = self.repository['testcontent']
        IPublishInfo(content).set_can_publish(CAN_PUBLISH_SUCCESS)
        IPublish(content).publish()
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        with self.assertRaises(LinkNotFoundError):
            b.getLink(url='@@rename-box')

        # Cannot rename even if one enters the URL manually
        b.open('http://localhost:8080/++skin++vivi/repository/testcontent/@@rename-box')
        with self.assertRaises(LookupError):
            b.getControl('Rename')  # 'Rename' button is missing

    def test_rename_menu_item_is_not_displayed_for_folder_with_content(self):
        folder = self.repository['testing']
        folder['foo'] = ExampleContentType()
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/repository/testing')
        with self.assertRaises(LinkNotFoundError):
            b.getLink(url='@@rename-box')

    def test_rename_folder_is_not_allowed_for_normal_user(self):
        self.repository['folder'] = Folder()
        b = self.browser
        b.open('/repository/folder')
        with self.assertRaises(LinkNotFoundError):
            b.getLink('Rename')
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open('@@rename-box')
            self.assertEqual(403, info.exception.status)

    def test_rename_success(self):
        b = self.browser
        b.open('/repository/testcontent')
        self.assertEllipsis('...lightbox_form...@@rename-box...', b.getLink('Rename').url)
        b.open('@@rename-box')

        self.assertEqual('testcontent', b.getControl('New file name').value)
        b.getControl('Rename').click()
        self.assertEllipsis('...testcontent...already exists...', b.contents)

        b.getControl('New file name').value = 'Sööö'.encode('utf-8')
        b.getControl('Rename').click()
        self.assertEllipsis('...Name contains invalid characters...', b.contents)

        b.getControl('New file name').value = 'renamed'
        b.getControl('Rename').click()
        self.assertEllipsis('...nextURL">.../repository/renamed...', b.contents)

        b.open('/repository/renamed')
        self.assertEllipsis('...Renamed "testcontent" to "renamed"...', b.contents)
