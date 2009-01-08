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
import zeit.connector.interfaces
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

    def setUp(self):
        super(Selenium, self).setUp()
        self.open_imp()

    def tearDown(self):
        super(Selenium, self).tearDown()
        self.selenium.open('http://%s/@@reset-mock-connector' %
                           self.selenium.server)

    def open_imp(self):
        self.selenium.open(
            'http://zmgr:mgrpw@%s/++skin++cms/repository/2006/'
            'DSC00109_2.JPG/@@imp.html' % self.selenium.server)

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' %
                            xml.sax.saxutils.quoteattr(label))


class BasicTests(Selenium):

    def test_generic_load(self):
        self.selenium.assertTextPresent('400x200')

    def test_crop_mask(self):
        s = self.selenium

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

        self.click_label("1px")
        s.verifyValue('//img[@id="imp-mask-image"]/@src', '')
        self.click_label("400x200")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width%3Aint=400&mask_height%3Aint=200&border=yes')

    def test_image_dragging(self):
        s = self.selenium
        s.verifyEval('window.document.imp.get_image_position()',
                     '{x: 1, y: 1}');
        s.dragAndDrop('id=imp-mask', '+30,+100')
        s.verifyEval('window.document.imp.get_image_position()',
                     '{x: 31, y: 101}');


class CropTests(Selenium):

    def test_crop_wo_mask(self):
        s = self.selenium
        s.verifyElementNotPresent('css=#imp-image-bar > div')
        s.comment('Nothing happens when the crop button is clicked.')
        s.click('crop')
        s.verifyElementNotPresent('css=#imp-image-bar > div')

    def test_crop(self):
        s = self.selenium
        s.verifyElementNotPresent('css=#imp-image-bar > div')
        s.dragAndDrop('id=imp-mask', '+30,+100')
        self.click_label("400x200")
        s.click('crop')
        s.comment('After cropping the image is inserted in the image bar')
        s.waitForElementPresent('css=#imp-image-bar > div')


class ResetMockConnector(object):

    def __call__(self):
        zope.component.getUtility(
            zeit.connector.interfaces.IConnector)._reset()
        return "Done."

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.imp.test.imp_layer))
    suite.addTest(unittest.makeSuite(ImageBarTest))
    return suite
