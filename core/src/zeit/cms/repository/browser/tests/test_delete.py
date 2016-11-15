from mechanize import LinkNotFoundError
from zeit.cms.testing import ZeitCmsBrowserTestCase
from zeit.cms.workflow.interfaces import IPublishInfo, IPublish
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS


class TestDeleteMenuItem(ZeitCmsBrowserTestCase):

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
        NotImplemented

    def test_delete_menu_item_is_not_displayed_for_folder_with_published_objects(self):
        NotImplemented

    def test_delete_menu_item_is_not_displayed_for_folder_with_subfolder(self):
        NotImplemented
