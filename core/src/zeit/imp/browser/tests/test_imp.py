# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import PIL.Image
import StringIO
import cjson
import pkg_resources
import transaction
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.image
import zeit.content.image.imagegroup
import zeit.content.image.interfaces
import zeit.content.image.tests
import zeit.imp.tests
import zope.app.file.image
import zope.app.testing.functional
import zope.component


class TestBase(zope.app.testing.functional.BrowserTestCase):

    layer = zeit.imp.tests.imp_layer
    image_path = '/++skin++cms/repository/group'
    auth = 'user:userpw'

    def setUp(self):
        super(TestBase, self).setUp()
        self.setSite(self.getRootFolder())
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        zeit.content.image.tests.create_image_group_with_master_image()

    def tearDown(self):
        del self.repository
        self.setSite(None)
        zeit.cms.testing.tearDown(self)
        super(TestBase, self).tearDown()


class ImageBarTest(TestBase):

    def get_image_bar_data(self):
        response = self.publish(
            self.image_path + '/@@imp-image-bar',
            basic=self.auth)
        return cjson.decode(response.getBody())

    def assertAPI(self, expected):
        self.assertEquals(expected, self.get_image_bar_data())

    def test_no_other_images_but_other_objects_return_empty_list(self):
        self.assertAPI([])

    def test_other_images(self):
        image = zeit.content.image.image.LocalImage()
        image.open('w').write(pkg_resources.resource_string(
            __name__, 'testdata/01.jpg'))
        self.repository['group']['foo-240x120.jpg'] = image
        self.assertAPI([{
            'url': 'http://localhost/++skin++cms/repository/group/foo-240x120.jpg',
            'name': 'foo-240x120.jpg',
            'scale_name': 'foo-240x120'}])

        # Another image
        image = zeit.content.image.image.LocalImage()
        image.open('w').write(pkg_resources.resource_string(
            __name__, 'testdata/02.jpg'))
        self.repository['group']['foo-artikel.jpg'] = image
        transaction.commit()
        self.assertAPI([
            {'url': 'http://localhost/++skin++cms/repository/group/foo-240x120.jpg',
             'name': 'foo-240x120.jpg',
             'scale_name': 'foo-240x120'},
            {'url': 'http://localhost/++skin++cms/repository/group/foo-artikel.jpg',
             'name': 'foo-artikel.jpg',
             'scale_name': 'foo-artikel'}])


class CropTest(TestBase):

    def get_image_data(self, **form):
        response = self.publish(
            self.image_path + '/@@imp-crop',
            basic=self.auth,
            form=dict(
                w='1000', h='500',
                x1='400', y1='100',
                x2='800', y2='300',
                name='400x200', **form))
        path = response.getBody().replace('http://localhost', '', 1)
        self.assertEqual('/++skin++cms/repository/group/group-400x200.jpg', path)
        return self.publish(path, basic=self.auth).getBody()

    def test_crop_returns_image_url(self):
        response = self.publish(
            self.image_path + '/@@imp-crop',
            basic=self.auth,
            form=dict(
                w='1200', h='749',
                x1='400', y1='100',
                x2='800', y2='300',
                name='400x200'))
        # The image name contains the parent name, the given name and .jpg
        self.assertEquals(
            'http://localhost/++skin++cms/repository/group/group-400x200.jpg',
            response.getBody())

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

        image = PIL.Image.open(StringIO.StringIO(image_data))
        # Verify some pixels around the border, they're all black:

        self.looks_black(image, 0,0)
        self.looks_black(image, 0, 1)
        self.looks_black(image, 0, 143)
        self.looks_black(image, 0, 199)
        self.looks_black(image, 399, 0)

    def test_crop_no_border_for_invalid_colours(self):
        # Basically makes only sure that we don't have an error.
        image_data = self.get_image_data(border='#asdf')

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
