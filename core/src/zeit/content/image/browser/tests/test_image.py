import zeit.cms.testing
import zeit.content.image.testing


class TestDelete(zeit.cms.testing.BrowserTestCase):
    """Test correct registration of delete views for images.

    This test must be done on an image (rather testcontent), since the adapter
    lookup was non-deterministic and "for example" broke for images. So we used
    images explicitely to test absence of weird behaviour.

    """

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_delete_message_in_repository(self):
        self.browser.open('http://localhost/++skin++vivi/repository/2006/'
                          'DSC00109_2.JPG/@@delete.html')
        self.assertEllipsis(
            '...Do you really want to delete the object from the folder...',
            self.browser.contents)

    def test_delete_message_in_workingcopy(self):
        self.browser.open('http://localhost/++skin++vivi/repository/2006/'
                          'DSC00109_2.JPG/@@checkout')
        self.browser.open('@@delete.html')
        self.assertEllipsis(
            '...Do you really want to delete your workingcopy?...',
            self.browser.contents)
