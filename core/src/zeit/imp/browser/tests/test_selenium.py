# coding: utf8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt


import subprocess
import sys
import webbrowser
import xml.sax.saxutils
import zc.selenium.pytest
import zeit.connector.interfaces
import zeit.content.image.test
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
        self.create_group()
        self.open_imp()

    def tearDown(self):
        super(Selenium, self).tearDown()
        self.selenium.open('http://%s/@@reset-mock-connector' %
                           self.selenium.server)

    def create_group(self):
        self.selenium.open(
            'http://zmgr:mgrpw@%s/++skin++cms/create-image-group' %
            self.selenium.server)

    def open_imp(self):
        self.selenium.open(
            'http://zmgr:mgrpw@%s/++skin++cms/repository/group/@@imp.html' %
            self.selenium.server)

    def click_label(self, label):
        self.selenium.click('//label[contains(string(.), %s)]' %
                            xml.sax.saxutils.quoteattr(label))


class SeleniumBasicTests(Selenium):

    def test_generic_load(self):
        self.selenium.assertTextPresent('450×200')

    def test_crop_mask(self):
        s = self.selenium

        s.comment('After clicking on the mask choice the image is loaded')
        self.click_label("450×200")
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
        self.click_label("450×200")
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
        s.runScript(
            'window.document.imp.parse_mask_string("500x200/500/200")');
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.name', '500x200')

        s.comment('The dimensions can be variable, indicated by a ?')
        s.runScript(
            'window.document.imp.parse_mask_string("art-200?500x200")');
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.mask_variable.w', 'true')
        s.verifyEval('window.document.imp.mask_variable.h', 'false')
        s.verifyEval('window.document.imp.name', 'art-200')

        s.runScript('window.document.imp.parse_mask_string("foo/?500/?200")');
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.mask_variable.w', 'true')
        s.verifyEval('window.document.imp.mask_variable.h', 'true')
        s.verifyEval('window.document.imp.name', 'foo')

    def test_zoom_slider(self):
        s = self.selenium
        s.comment('Zooming works with a slider')
        s.verifyEval('window.document.imp.zoom>1', 'false')
        s.clickAt('id=imp-zoom-slider', '200,0')
        s.verifyEval('window.document.imp.zoom>1', 'true')

    def test_zoom_mouse_wheel(self):
        s = self.selenium
        s.verifyEval('window.document.imp.zoom.toPrecision(3)', '0.268')
        self.zoom_with_wheel(10000)
        s.verifyEval('window.document.imp.zoom>1', 'true')
        self.zoom_with_wheel(-5000)
        s.verifyEval('window.document.imp.zoom<1', 'true')
        s.verifyEval('window.document.imp.zoom>0.268', 'true')

    def test_zoom_with_mouse_wheel_updates_slider(self):
        s = self.selenium
        s.verifyEval('window.document.imp_zoom_slider.get_value()>1', 'false')
        self.zoom_with_wheel(10000)
        s.verifyEval('window.document.imp_zoom_slider.get_value()>1', 'true')

    def zoom_with_wheel(self, delta_y):
        self.selenium.runScript(
        """\
            var evt = window.document.createEvent('MouseEvents');
            evt.initEvent('DOMMouseScroll', false, false);
            evt.wheelDeltaX = 0;
            evt.wheelDeltaY = %s;
            window.document.getElementById('imp-mask').dispatchEvent(evt);
        """ % delta_y);


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
        s.verifyElementNotPresent('css=label.cropped')
        s.dragAndDrop('id=imp-mask', '+30,+100')
        self.click_label("450×200")
        s.click('crop')
        s.comment('After cropping the image is inserted in the image bar')
        s.waitForElementPresent('css=#imp-image-bar > div')
        s.comment('The label is marked as "cropped"')
        s.verifyElementPresent('css=label.cropped')


class SeleniumMaskTests(Selenium):

    def test_input_fields_show_mask_size(self):
        s = self.selenium
        self.click_label("450×200")
        s.verifyValue('mask-w', '450')
        s.verifyValue('mask-h', '200')
        self.click_label("210×210")
        s.verifyValue('mask-w', '210')
        s.verifyValue('mask-h', '210')

    def test_input_fields_disabled_for_fixed_mask(self):
        s = self.selenium
        self.click_label("450×200")
        s.storeEval(
            "window.document.getElementById('imp-configuration-form')", 'form')
        s.verifyEval("storedVars['form']['mask-w'].disabled", 'true');
        s.verifyEval("storedVars['form']['mask-h'].disabled", 'true');

    def test_input_fields_initally_disabled(self):
        s = self.selenium
        s.storeEval(
            "window.document.getElementById('imp-configuration-form')", 'form')
        s.verifyEval("storedVars['form']['mask-w'].disabled", 'true');
        s.verifyEval("storedVars['form']['mask-h'].disabled", 'true');

    def test_input_field_enabled_for_variable_mask(self):
        s = self.selenium
        self.click_label("Artikelbild breit")
        s.storeEval(
            "window.document.getElementById('imp-configuration-form')", 'form')
        s.verifyEval("storedVars['form']['mask-w'].disabled", 'true');
        s.verifyEval("storedVars['form']['mask-h'].disabled", 'false');

    def test_input_field_changes_are_reflected_in_the_mask(self):
        s = self.selenium
        self.click_label("Artikelbild breit")
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.type('mask-h', '280')
        s.verifyEval('window.document.imp.mask_dimensions.h', '280')

    def test_input_field_up_arrow_once_handling(self):
        self.selenium.comment('Pressing UP-ARROW once increases by 1.')
        self.verify_press('\\38', '201')

    def test_input_field_down_arrow_once_handling(self):
        self.selenium.comment('Pressing DOWN-ARROW once decreases by 1.')
        self.verify_press('\\40', '199')

    def test_input_field_left_arrow_once_handling(self):
        self.selenium.comment('Pressing LEFT-ARROW once decreases by 1.')
        self.verify_press('\\37', '199')

    def test_input_field_right_arrow_once_handling(self):
        self.selenium.comment('Pressing RIGHT-ARROW once increases by 1.')
        self.verify_press('\\39', '201')

    def verify_press(self, key_code, expected_value):
        s = self.selenium
        self.click_label("Artikelbild breit")
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.keyDown('mask-h', key_code)
        s.keyUp('mask-h', key_code)
        s.verifyEval('window.document.imp.mask_dimensions.h', expected_value)

    def test_input_field_up_arrow_hold_handling(self):
        self.selenium.comment('Holding UP-ARROW increases.')
        self.verify_hold('\\38', '>210')

    def test_input_field_down_arrow_hold_handling(self):
        self.selenium.comment('Holding DOWN-ARROW decreases.')
        self.verify_hold('\\40', '<190')

    def test_input_field_left_arrow_hold_handling(self):
        self.selenium.comment('Holding LEFT-ARROW decreases.')
        self.verify_hold('\\37', '<190')

    def test_input_field_right_arrow_hold_handling(self):
        self.selenium.comment('Holding RIGHT-ARROW increases.')
        self.verify_hold('\\39', '>210')

    def verify_hold(self, key_code, expected_value):
        s = self.selenium
        self.click_label("Artikelbild breit")
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.keyDown('mask-h', key_code)
        s.pause('5000')
        s.keyUp('mask-h', key_code)
        s.verifyEval(
            'window.document.imp.mask_dimensions.h %s' % expected_value,
            'true')


class ResetMockConnector(object):

    def __call__(self):
        zope.component.getUtility(
            zeit.connector.interfaces.IConnector)._reset()
        return "Done."


class CreateImageGroup(object):

    def __call__(self):
        zeit.content.image.test.create_image_group_with_master_image()
