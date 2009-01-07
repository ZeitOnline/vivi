# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import pkg_resources
import subprocess
import transaction
import unittest
import webbrowser
import xml.sax.saxutils
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

    def open_imp(self):
        self.selenium.open(
            'http://zmgr:mgrpw@%s/++skin++cms/repository/2006/'
            'DSC00109_2.JPG/@@imp.html' % self.selenium.server)

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' %
                            xml.sax.saxutils.quoteattr(label))


    def test_generic_load(self):
        self.open_imp()
        self.selenium.assertTextPresent('400x200')

    def test_crop_mask(self):
        s = self.selenium
        self.open_imp()

        s.comment('After clicking on the mask choice the image is loaded')
        self.click_label("400x200")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width%3Aint=400&mask_height%3Aint=200&border=')

        s.comment('The border will be passed')
        self.click_label("Border")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width%3Aint=400&mask_height%3Aint=200&border=yes')

    def test_border_select_wo_selected_mask_does_not_fail(self):
        s = self.selenium
        self.open_imp()

        self.click_label("1px")
        s.verifyValue('//img[@id="imp-mask-image"]/@src', '')
        self.click_label("400x200")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width%3Aint=400&mask_height%3Aint=200&border=yes')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.imp.test.imp_layer))
    suite.addTest(unittest.makeSuite(ImageBarTest))
    return suite
