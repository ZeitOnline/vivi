from urllib.parse import urlencode
from io import BytesIO
import PIL.Image
import json
import pkg_resources
import transaction
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.testing
import zeit.imp.tests
import zope.app.file.image
import zope.component
import zope.component.hooks


class TestBase(zeit.imp.tests.BrowserTestCase):

    image_path = 'http://localhost/++skin++cms/repository/group'

    def setUp(self):
        super().setUp()
        zope.component.hooks.setSite(self.getRootFolder())
        zeit.content.image.testing.create_image_group_with_master_image()


class ImageBarTest(TestBase):

    def get_image_bar_data(self):
        self.browser.open(self.image_path + '/@@imp-image-bar')
        return json.loads(self.browser.contents)

    def assertAPI(self, expected):
        self.assertEqual(expected, self.get_image_bar_data())

    def test_no_other_images_but_other_objects_return_empty_list(self):
        self.assertAPI([])

    def test_other_images(self):
        image = zeit.content.image.image.LocalImage()
        with image.open('w') as f:
            f.write(pkg_resources.resource_string(
                __name__, 'testdata/01.jpg'))
        self.repository['group']['foo-240x120.jpg'] = image
        self.assertAPI([{
            'url':
            'http://localhost/++skin++cms/repository/group/foo-240x120.jpg',
            'name': 'foo-240x120.jpg',
            'scale_name': 'foo-240x120'}])

        # Another image
        image = zeit.content.image.image.LocalImage()
        with image.open('w') as f:
            f.write(pkg_resources.resource_string(
                __name__, 'testdata/02.jpg'))
        self.repository['group']['foo-artikel.jpg'] = image
        transaction.commit()
        self.assertAPI([
            {'url':
             'http://localhost/++skin++cms/repository/group/foo-240x120.jpg',
             'name': 'foo-240x120.jpg',
             'scale_name': 'foo-240x120'},
            {'url':
             'http://localhost/++skin++cms/repository/group/foo-artikel.jpg',
             'name': 'foo-artikel.jpg',
             'scale_name': 'foo-artikel'}])


class CropTest(TestBase):

    def get_image_data(self, **form):
        self.browser.post(
            self.image_path + '/@@imp-crop', urlencode(dict(
                w='1000', h='500',
                x1='400', y1='100',
                x2='800', y2='300',
                name='400x200', **form)))
        path = self.browser.contents.replace('http://localhost', '', 1)
        self.assertEqual(
            '/++skin++cms/repository/group/group-400x200.jpg', path)
        self.browser.open(path + '/@@raw')
        return self.browser.contents

    def test_crop_returns_image_url(self):
        self.browser.post(
            self.image_path + '/@@imp-crop', urlencode(dict(
                w='1200', h='749',
                x1='400', y1='100',
                x2='800', y2='300',
                name='400x200')))
        # The image name contains the parent name, the given name and .jpg
        self.assertEqual(
            'http://localhost/++skin++cms/repository/group/group-400x200.jpg',
            self.browser.contents)

    def test_crop_size(self):
        image_data = self.get_image_data()
        self.assertEqual(
            ('image/jpeg', 400, 200),
            zope.app.file.image.getImageInfo(image_data))

    def test_crop_border(self):
        image_data = self.get_image_data(border='#000000')
        # A border does not change the image size, the border is *inside*
        self.assertEqual(
            ('image/jpeg', 400, 200),
            zope.app.file.image.getImageInfo(image_data))

        image = PIL.Image.open(BytesIO(image_data))
        # Verify some pixels around the border, they're all black:

        self.looks_black(image, 0, 0)
        self.looks_black(image, 0, 1)
        self.looks_black(image, 0, 143)
        self.looks_black(image, 0, 199)
        self.looks_black(image, 399, 0)

    def test_crop_no_border_for_invalid_colours(self):
        # Basically makes only sure that we don't have an error.
        self.get_image_data(border='#asdf')

    def looks_black(self, img, x, y):
        # The pixels are not really black because we've got a jpeg.
        color = img.getpixel((x, y))
        self.assertTrue(
            sum(color) < 70, "fail %s, %s sum%s > 70" % (x, y, color))

    def test_filters_applied(self):
        # Test that the image is different with and without a filter applied
        img1 = self.get_image_data()
        img2 = self.get_image_data(**{'filter.brightness': '0.5'})
        self.assertNotEqual(img1, img2)
