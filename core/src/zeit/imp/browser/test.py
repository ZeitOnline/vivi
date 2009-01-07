# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import pkg_resources
import subprocess
import transaction
import unittest
import webbrowser
import zc.selenium.pytest
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.imp.test
import zope.app.testing.functional
import zope.component


class MacOSXFirefox(webbrowser.BaseBrowser):

    def open(self, url, new=0, autoraise=1):
        proc = subprocess.Popen(
            ['/usr/bin/open', '-a', 'Firefox', url])
        proc.communicate()


webbrowser.register('Firefox', MacOSXFirefox, None, -1)


class ImageBarTest(zope.app.testing.functional.BrowserTestCase):

    layer=zeit.imp.test.imp_layer

    def setUp(self):
        super(ImageBarTest, self).setUp()
        self.setSite(self.getRootFolder())
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def tearDown(self):
        del self.repository
        self.setSite(None)
        super(ImageBarTest, self).tearDown()

    def get_image_bar_data(self):
        response = self.publish(
            '/++skin++cms/repository/2006/DSC00109_2.JPG/@@imp-image-bar',
            basic='user:userpw')
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


class Selenium(zc.selenium.pytest.Test):

    def test_generic_load(self):
        s = self.selenium
        s.open('http://zmgr:mgrpw@%s/++skin++cms/repository/2006/'
               'DSC00109_2.JPG/@@imp.html' % s.server)
        s.assertTextPresent('400x200')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.imp.test.imp_layer))
    suite.addTest(unittest.makeSuite(ImageBarTest))
    return suite
