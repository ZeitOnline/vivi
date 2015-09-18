import ZODB.utils
import os.path
import unittest
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


class ImageEdit(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(ImageEdit, self).setUp()
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository'
            '/2006/DSC00109_2.JPG/@@checkout')
        b.getControl(
            name='form.copyrights.0..combination_00').value = 'required'

    @unittest.skip(
        'Disabled because the frontend does not interpret rewritten links '
        'correctly yet.')
    def test_rewrites_links_from_www_zeit_de_to_xml_zeit_de(self):
        b = self.browser
        b.getControl('Links to').value = 'http://www.zeit.de/foo/bar'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual(
            'http://xml.zeit.de/foo/bar', b.getControl('Links to').value)

    def test_leaves_other_links_alone(self):
        b = self.browser
        b.getControl('Links to').value = 'http://example.de/foo/bar'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual(
            'http://example.de/foo/bar', b.getControl('Links to').value)
