# coding: utf-8
import pkg_resources
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


class TestImage(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_normalizes_filename_on_upload(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/2006/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image (single)']
        b.open(menu.value[0])

        b.getControl(name='form.copyrights.0..combination_00').value = (
            'ZEIT ONLINE')
        b.getControl(name='form.copyrights.0..combination_03').value = (
            'http://www.zeit.de/')
        b.getControl(name='form.blob').add_file(
            pkg_resources.resource_stream(
                'zeit.content.image.browser',
                'testdata/new-hampshire-artikel.jpg'),
            'image/jpeg', u'föö.jpg'.encode('utf-8'))
        b.getControl(name='form.actions.add').click()
        self.assertIn('/foeoe.jpg/@@edit.html', b.url)
