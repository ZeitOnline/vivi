# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt


import subprocess
import sys
import webbrowser
import xml.sax.saxutils
import zc.selenium.pytest
import zeit.connector.interfaces
import zope.component


if sys.platform == 'darwin':
    # Register a Firefox browser for Mac OS X.
    class MacOSXFirefox(webbrowser.BaseBrowser):

        def open(self, url, new=0, autoraise=1):
            proc = subprocess.Popen(
                ['/usr/bin/open', '-a', 'Firefox', url])
            proc.communicate()
    webbrowser.register('Firefox', MacOSXFirefox, None, -1)


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


class SeleniumBasicTests(Selenium):

    def test_generic_load(self):
        self.selenium.assertTextPresent('450x200')

    def test_crop_mask(self):
        s = self.selenium

        s.comment('After clicking on the mask choice the image is loaded')
        self.click_label("450x200")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=')

        s.comment('The border will be passed')
        self.click_label("Border")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=yes')

    def test_border_select_wo_selected_mask_does_not_fail(self):
        s = self.selenium

        self.click_label("1px")
        s.verifyValue('//img[@id="imp-mask-image"]/@src', '')
        self.click_label("450x200")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=yes')

    def test_image_dragging(self):
        s = self.selenium
        s.verifyEval('window.document.imp.get_image_position()',
                     '{x: 1, y: 1}');
        s.dragAndDrop('id=imp-mask', '+30,+100')
        s.verifyEval('window.document.imp.get_image_position()',
                     '{x: 31, y: 101}');

    def test_mask_string_parse(self):
        s = self.selenium

        s.comment('Simple dimensions')
        s.runScript('window.document.imp.parse_mask_string("500x200")');
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')

        s.comment('The dimensions can be variable, indicated by a ?')
        s.runScript('window.document.imp.parse_mask_string("?500x200")');
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.mask_variable.w', 'true')
        s.verifyEval('window.document.imp.mask_variable.h', 'false')

        s.runScript('window.document.imp.parse_mask_string("?500x?200")');
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.mask_variable.w', 'true')
        s.verifyEval('window.document.imp.mask_variable.h', 'true')


class SeleniumCropTests(Selenium):

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
        self.click_label("450x200")
        s.click('crop')
        s.comment('After cropping the image is inserted in the image bar')
        s.waitForElementPresent('css=#imp-image-bar > div')


class ResetMockConnector(object):

    def __call__(self):
        zope.component.getUtility(
            zeit.connector.interfaces.IConnector)._reset()
        return "Done."
