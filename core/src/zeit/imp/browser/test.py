# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import pkg_resources
import transaction
import unittest
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.imp.test
import zope.app.testing.functional
import zope.app.file.image
import zope.component


class TestBase(zope.app.testing.functional.BrowserTestCase):

    layer=zeit.imp.test.imp_layer
    image_path = '/++skin++cms/repository/2006/DSC00109_2.JPG'
    auth = 'user:userpw'

    def setUp(self):
        super(TestBase, self).setUp()
        self.setSite(self.getRootFolder())
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def tearDown(self):
        del self.repository
        self.setSite(None)
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
        self.repository['2006']['foo-240x120.jpg'] = image
        self.assertAPI([{
            'url': 'http://localhost/++skin++cms/repository/2006/foo-240x120.jpg',
            'name': 'foo-240x120.jpg'}])

        # Another image
        image = zeit.content.image.image.LocalImage()
        image.open('w').write(pkg_resources.resource_string(
            __name__, 'testdata/02.jpg'))
        self.repository['2006']['foo-artikel.jpg'] = image
        transaction.commit()
        self.assertAPI([
            {'url': 'http://localhost/++skin++cms/repository/2006/foo-240x120.jpg',
             'name': 'foo-240x120.jpg'},
            {'url': 'http://localhost/++skin++cms/repository/2006/foo-artikel.jpg',
             'name': 'foo-artikel.jpg'}])


class CropTest(TestBase):

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
            'http://localhost/++skin++cms/repository/2006/2006-400x200.jpg',
            response.getBody())

    def test_crop_size(self):
        response = self.publish(
            self.image_path + '/@@imp-crop',
            basic=self.auth,
            form=dict(
                w='1000', h='500',
                x1='400', y1='100',
                x2='800', y2='300',
                name='400x200'))
        path = response.getBody().replace('http://localhost', '', 1)
        self.assertEqual('/++skin++cms/repository/2006/2006-400x200.jpg', path)
        image_data = self.publish(path, basic=self.auth).getBody()
        self.assertEqual(
            ('image/jpeg', 400, 200),
            zope.app.file.image.getImageInfo(image_data))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.imp.test.imp_layer))
    suite.addTest(unittest.makeSuite(ImageBarTest))
    suite.addTest(unittest.makeSuite(CropTest))
    return suite
