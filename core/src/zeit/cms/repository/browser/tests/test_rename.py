from zope.testbrowser.browser import LinkNotFoundError

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS, IPublish, IPublishInfo
import zeit.cms.testing


class TestRenameMenuItem(zeit.cms.testing.ZeitCmsBrowserTestCase):
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
        b.open('http://localhost:8080/++skin++vivi/repository/testcontent' '/@@rename-box')
        with self.assertRaises(LookupError):
            b.getControl('Rename')  # 'Rename' button is missing

    def test_rename_menu_item_is_not_displayed_for_folder_with_content(self):
        folder = self.repository['testing']
        folder['foo'] = ExampleContentType()
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/repository/testing')
        with self.assertRaises(LinkNotFoundError):
            b.getLink(url='@@rename-box')
