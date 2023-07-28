# coding: utf-8
from zeit.content.image.testing import fixture_bytes
import zeit.content.image.testing


class TestDelete(zeit.content.image.testing.BrowserTestCase):
    """Test correct registration of delete views for images.

    This test must be done on an image (rather testcontent), since the adapter
    lookup was non-deterministic and "for example" broke for images. So we used
    images explicitely to test absence of weird behaviour.

    """

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


class TestImage(zeit.content.image.testing.BrowserTestCase):

    def test_normalizes_filename_on_upload(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/2006/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image (single)']
        b.open(menu.value[0])
        b.getControl(name='form.copyright.combination_00').value = (
            'ZEIT ONLINE')
        b.getControl(name='form.copyright.combination_01').displayValue = (
            ['dpa'])
        b.getControl(name='form.copyright.combination_03').value = (
            'http://www.zeit.de/')

        b.getControl(name='form.blob').add_file(
            fixture_bytes('new-hampshire-artikel.jpg'),
            'image/jpeg', 'föö.jpg'.encode('utf-8'))
        b.getControl(name='form.actions.add').click()
        self.assertIn('/foeoe.jpg/@@edit.html', b.url)

    def test_rejects_unsupported_mime_types_on_upload(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/2006/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image (single)']
        b.open(menu.value[0])
        b.getControl(name='form.copyright.combination_00').value = (
            'ZEIT ONLINE')
        b.getControl(name='form.copyright.combination_01').displayValue = (
            ['dpa'])
        b.getControl(name='form.copyright.combination_03').value = (
            'http://www.zeit.de/')

        b.getControl(name='form.blob').add_file(fixture_bytes(
            'berlin-polizei.webp'), 'image/webp', 'foo.webp')
        b.getControl(name='form.actions.add').click()
        self.assertEllipsis('...Unsupported image type...', b.contents)

    def test_resizes_too_large_image_on_upload_width(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/2006/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image (single)']
        b.open(menu.value[0])
        b.getControl(name='form.copyright.combination_00').value = (
            'ZEIT ONLINE')
        b.getControl(name='form.copyright.combination_01').displayValue = (
            ['dpa'])
        b.getControl(name='form.copyright.combination_03').value = (
            'http://www.zeit.de/')

        b.getControl(name='form.blob').add_file(
            fixture_bytes('shoppingmeile_2251x4001px.jpg'),
            'image/jpeg', 'föö.jpg'.encode('utf-8'))
        b.getControl(name='form.actions.add').click()
        img = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/foeoe.jpg')
        assert(img.getImageSize()) == (2250, 4000)

    def test_resizes_too_large_image_on_upload_height(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/2006/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image (single)']
        b.open(menu.value[0])
        b.getControl(name='form.copyright.combination_00').value = (
            'ZEIT ONLINE')
        b.getControl(name='form.copyright.combination_01').displayValue = (
            ['dpa'])
        b.getControl(name='form.copyright.combination_03').value = (
            'http://www.zeit.de/')

        b.getControl(name='form.blob').add_file(
            fixture_bytes('shoppingmeile_4001x2251px.jpg'),
            'image/jpeg', 'bär.jpg'.encode('utf-8'))
        b.getControl(name='form.actions.add').click()
        img = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/baer.jpg')
        assert(img.getImageSize()) == (4000, 2250)
