# coding: utf8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.connector.interfaces
import zeit.content.image.tests
import zeit.cms.testing
import gocept.selenium.ztk
import zeit.imp.tests


Layer = gocept.selenium.ztk.Layer(zeit.imp.tests.imp_layer)


class Selenium(zeit.cms.testing.SeleniumTestCase):

    layer = Layer
    window_width = 1100
    window_height = 600

    def setUp(self):
        super(Selenium, self).setUp()
        self.create_group()
        s = self.selenium
        # Set the size to a defined value
        s.getEval('window.resizeTo(%s, %s)' % (
            self.window_width, self.window_height))
        s.waitForEval('window.outerWidth', str(self.window_width))
        s.waitForEval('window.outerHeight', str(self.window_height))
        self.open_imp()

    def create_group(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            zeit.content.image.tests.create_image_group_with_master_image()

    def open_imp(self):
        self.open('/repository/group/@@imp.html')


class SeleniumBasicTests(Selenium):

    def test_generic_load(self):
        self.selenium.assertTextPresent(u'450×200')

    def test_crop_mask(self):
        s = self.selenium

        #s.comment('After clicking on the mask choice the image is loaded')
        self.click_label(u"450×200")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=')

        #s.comment('The border will be passed')
        self.click_label("grauer Rahmen")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=%23888888')

    def test_border_select_wo_selected_mask_does_not_fail(self):
        s = self.selenium

        self.click_label("schwarzer Rahmen")
        s.verifyElementNotPresent('id=imp-mask-image')
        self.click_label(u"450×200")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=%23000000')

    def test_image_dragging(self):
        s = self.selenium
        s.verifyEval('window.document.imp.get_image_position()',
                     '{x: 1, y: 1}')
        s.dragAndDrop('id=imp-mask', '+30,+100')
        s.verifyEval('window.document.imp.get_image_position()',
                     '{x: 31, y: 101}')

    def test_mask_string_parse(self):
        s = self.selenium

        #s.comment('Simple dimensions')
        s.runScript(
            'window.document.imp.set_mask("500x200/500/200")')
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.name', '500x200')

        #s.comment('The dimensions can be variable, indicated by a ?')
        s.runScript(
            'window.document.imp.set_mask("art-200/?500/200")')
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.mask_variable.w', 'true')
        s.verifyEval('window.document.imp.mask_variable.h', 'false')
        s.verifyEval('window.document.imp.name', 'art-200')

        s.runScript('window.document.imp.set_mask("foo/?500/?200")')
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.mask_variable.w', 'true')
        s.verifyEval('window.document.imp.mask_variable.h', 'true')
        s.verifyEval('window.document.imp.name', 'foo')

    def test_zoom_slider(self):
        s = self.selenium
        #s.comment('Zooming works with a slider')
        s.verifyEval('window.document.imp.zoom>1', 'false')
        s.clickAt('id=imp-zoom-slider', '500,0')
        s.waitForEval('window.document.imp.zoom>1', 'true')

    def test_zoom_mouse_wheel(self):
        s = self.selenium
        zoom = float(s.getEval('window.document.imp.zoom.toPrecision(3)'))
        self.zoom_with_wheel(10000)
        self.assertTrue(float(s.getEval('window.document.imp.zoom')) > 1)
        self.zoom_with_wheel(-9000)
        self.assertTrue(float(s.getEval('window.document.imp.zoom')) < 1)
        self.assertTrue(float(s.getEval('window.document.imp.zoom')) > zoom)

    def test_zoom_with_mouse_wheel_updates_slider(self):
        s = self.selenium
        s.verifyEval('window.document.imp_zoom_slider.get_value()>1', 'false')
        self.zoom_with_wheel(10000)
        s.verifyEval('window.document.imp_zoom_slider.get_value()>1', 'true')

    def zoom_with_wheel(self, delta_y):
        self.selenium.runScript(
        """\
            var evt = window.document.createEvent('MouseEvents')
            evt.initEvent('DOMMouseScroll', false, false)
            evt.wheelDeltaX = 0;
            evt.wheelDeltaY = %s;
            window.document.getElementById('imp-mask').dispatchEvent(evt)
        """ % delta_y)


class SeleniumCropTests(Selenium):

    def test_crop_wo_mask(self):
        s = self.selenium
        s.verifyElementNotPresent('css=#imp-image-bar > div')
        #s.comment('Nothing happens when the crop button is clicked.')
        s.click('crop')
        s.verifyElementNotPresent('css=#imp-image-bar > div')

    def test_crop(self):
        s = self.selenium
        s.verifyElementNotPresent('css=#imp-image-bar > div')
        s.verifyElementNotPresent('css=label.cropped')
        s.dragAndDrop('id=imp-mask', '-30,-100')
        self.click_label(u"450×200")
        s.click('crop')
        #s.comment('After cropping the image is inserted in the image bar')
        s.waitForElementPresent('css=#imp-image-bar > div')
        #s.comment('The label is marked as "cropped"')
        s.verifyElementPresent('css=label.cropped')

    def test_crop_outside_mask(self):
        s = self.selenium
        s.verifyElementNotPresent('css=#imp-image-bar > div')
        s.verifyElementNotPresent('css=label.cropped')
        self.click_label(u"450×200")
        s.clickAt('id=imp-zoom-slider', '1,0')
        s.click('crop')
        s.verifyAlert('Das Bild ist nicht*')
        s.verifyElementNotPresent('css=#imp-image-bar > div')

    def test_drag_outside_mask_snaps_to_mask(self):
        # As it snaps to the mask we can crop the image and no alert is
        # generated.
        s = self.selenium
        self.click_label(u"450×200")
        s.dragAndDrop('id=imp-mask', '+1000,+1000')
        s.click('crop')
        s.waitForElementPresent('css=#imp-image-bar > div')


class SeleniumMaskTests(Selenium):

    def test_input_fields_show_mask_size(self):
        s = self.selenium
        self.click_label(u"450×200")
        s.verifyValue('mask-w', '450')
        s.verifyValue('mask-h', '200')
        self.click_label(u"210×210")
        s.verifyValue('mask-w', '210')
        s.verifyValue('mask-h', '210')

    def test_input_fields_disabled_for_fixed_mask(self):
        s = self.selenium
        self.click_label(u"450×200")
        form = "window.document.getElementById('imp-configuration-form')"
        s.verifyEval("%s['mask-w'].disabled" % form, 'true')
        s.verifyEval("%s['mask-h'].disabled" % form, 'true')

    def test_input_fields_initally_disabled(self):
        s = self.selenium
        form = "window.document.getElementById('imp-configuration-form')"
        s.verifyEval("%s['mask-w'].disabled" % form, 'true')
        s.verifyEval("%s['mask-h'].disabled" % form, 'true')

    def test_input_field_enabled_for_variable_mask(self):
        s = self.selenium
        self.click_label("Artikelbild breit")
        form = "window.document.getElementById('imp-configuration-form')"
        s.verifyEval("%s['mask-w'].disabled" % form, 'true')
        s.verifyEval("%s['mask-h'].disabled" % form, 'false')

    def test_input_field_changes_are_reflected_in_the_mask(self):
        s = self.selenium
        self.click_label("Artikelbild breit")
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.type('mask-h', '280')
        s.verifyEval('window.document.imp.mask_dimensions.h', '280')

    def test_input_field_up_arrow_once_handling_should_increase_by_1(self):
        self.verify_press('\\38', '201')

    def test_input_field_down_arrow_once_handling(self):
        #self.selenium.comment('Pressing DOWN-ARROW once decreases by 1.')
        self.verify_press('\\40', '199')

    def test_input_field_left_arrow_once_handling(self):
        #self.selenium.comment('Pressing LEFT-ARROW once decreases by 1.')
        self.verify_press('\\37', '199')

    def test_input_field_right_arrow_once_handling(self):
        #self.selenium.comment('Pressing RIGHT-ARROW once increases by 1.')
        self.verify_press('\\39', '201')

    def verify_press(self, key_code, expected_value):
        s = self.selenium
        self.click_label("Artikelbild breit")
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.keyDown('mask-h', key_code)
        s.keyUp('mask-h', key_code)
        s.verifyEval('window.document.imp.mask_dimensions.h', expected_value)

    def test_input_field_up_arrow_hold_handling(self):
        #self.selenium.comment('Holding UP-ARROW increases.')
        self.verify_hold('\\38', '>210')

    def test_input_field_down_arrow_hold_handling(self):
        #self.selenium.comment('Holding DOWN-ARROW decreases.')
        self.verify_hold('\\40', '<190')

    def test_input_field_left_arrow_hold_handling(self):
        #self.selenium.comment('Holding LEFT-ARROW decreases.')
        self.verify_hold('\\37', '<190')

    def test_input_field_right_arrow_hold_handling(self):
        #self.selenium.comment('Holding RIGHT-ARROW increases.')
        self.verify_hold('\\39', '>210')

    def verify_hold(self, key_code, expected_value):
        s = self.selenium
        self.click_label("Artikelbild breit")
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.keyDown('mask-h', key_code)
        s.pause(5000)
        s.keyUp('mask-h', key_code)
        s.verifyEval(
            'window.document.imp.mask_dimensions.h %s' % expected_value,
            'true')

    def test_mask_select_should_fit_image_into_mask_x(self):
        s = self.selenium
        self.click_label('Artikelbild breit')
        s.verifyEval('window.document.imp.mask_dimensions.w', '410')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        # X fits
        s.verifyEval('window.document.imp.get_crop_arguments().x1', '0')
        s.verifyEval('window.document.imp.get_crop_arguments().x2', '410')
        # Y is aligned middle
        s.verifyEval('window.document.imp.get_crop_arguments().y1', '53')
        s.verifyEval('window.document.imp.get_crop_arguments().y2', '253')

    def test_mask_select_should_fit_image_into_mask_y(self):
        s = self.selenium
        self.click_label('Audio')
        s.verifyEval('window.document.imp.mask_dimensions.w', '180')
        s.verifyEval('window.document.imp.mask_dimensions.h', '180')
        # X is aligned centered
        s.verifyEval('window.document.imp.get_crop_arguments().x1', '30')
        s.verifyEval('window.document.imp.get_crop_arguments().x2', '210')
        # Y fits
        s.verifyEval('window.document.imp.get_crop_arguments().y1', '0')
        s.verifyEval('window.document.imp.get_crop_arguments().y2', '180')


class ResizeTests(Selenium):

    window_width = 1000
    window_height = 800

    def setUp(self):
        super(ResizeTests, self).setUp()
        # Choose a mask
        self.click_label(u"450×200")

    def test_window_resize_updates_mask(self):
        s = self.selenium
        # Store the current mask image dimensions
        width = int(s.getEval('window.document.imp.mask_image_dimensions.w'))
        height = int(s.getEval('window.document.imp.mask_image_dimensions.h'))
        # Increase the window width affects mask, try width only first:
        s.getEval('window.resizeTo(1200, 800)')
        s.waitForEval(
            "window.document.imp.mask_image_dimensions.w > %d" % width,
            'true')
        self.assertEqual(
            height,
            int(s.getEval("window.document.imp.mask_image_dimensions.h")))

        # change width and height:
        s.getEval('window.resizeTo(800, 900)')
        s.pause(100)
        s.waitForEval(
            "window.document.imp.mask_image_dimensions.w < %d" % width,
            'true')
        self.assertTrue(
            int(s.getEval("window.document.imp.mask_image_dimensions.h"))
            > height)

    def test_window_resize_moves_image(self):
        # When the area changes it's size the crop area remains centered. This
        # means we must move the image to not change the current view. That
        # means that after changing the size, the crop parameters remain the
        # same.

        s = self.selenium
        get_crop_args = ('window.MochiKit.Base.serializeJSON('
                         '  window.document.imp.get_crop_arguments())')
        crop_args = s.getEval(get_crop_args)

        s.getEval('window.resizeTo(900, 900)')
        s.pause(500)
        s.waitForEval(get_crop_args, crop_args)

        # Try another one, to be sure this works multiple times
        s.getEval('window.resizeTo(1000, 800)')
        s.pause(500)
        s.waitForEval("%s == '%s'" % (get_crop_args, crop_args), 'true')

    def test_window_resize_updates_zoom_slider(self):
        # The zoom slider doesn't automatically support size updates.
        s = self.selenium
        max_left = s.getEval(
            'window.document.imp_zoom_slider.zoom_slider._maxLeft')
        s.getEval('window.parent.resizeTo(800, 900)')
        s.waitForEval(
            'window.document.imp_zoom_slider.zoom_slider._maxLeft < %s' %
            max_left, 'true')

    def test_sidebar_switch_sends_resize_event(self):
        # The sidebar can be switched on/off. This obiously doesn't send an
        # onresize event to the window. We must support this nevertheless.

        s = self.selenium
        max_left = s.getEval(
            'window.document.imp_zoom_slider.zoom_slider._maxLeft')
        s.click('id=sidebar-dragger')
        s.pause(50)
        s.waitForEval(
            'window.document.imp_zoom_slider.zoom_slider._maxLeft > %s' %
            max_left, 'true')
        # Clicking again resets to the original state
        s.click('id=sidebar-dragger')
        s.pause(50)
        s.waitForEval(
            'window.document.imp_zoom_slider.zoom_slider._maxLeft == %s' %
            max_left, 'true')


class FilterTests(Selenium):

    def test_value_mapper(self):
        s = self.selenium

        def verify_mappers(step, value, filter):
            s.waitForNotEval(
                'typeof(window.document.imp_color_filter)', 'undefined')
            s.verifyEval(
                'window.document.imp_color_filter.to_value(%s)' % step,
                str(value))
            s.verifyEval(
                'window.document.imp_color_filter.to_step(%s)' % value,
                str(step))
            s.verifyEval(
                'window.document.imp_color_filter.to_filter(%s)' % value,
                str(filter))

        verify_mappers(0, -100, 0.75)
        verify_mappers(600, -40, 0.9)
        verify_mappers(1000, 0, 1)
        verify_mappers(1800, 80, 2)
        verify_mappers(2000, 100, 2.25)

    def test_brightness_slider(self):
        self.verify_slider('brightness')

    def test_contrast_slider(self):
        self.verify_slider('contrast')

    def test_color_slider(self):
        self.verify_slider('color')

    def test_sharpness_slider(self):
        self.verify_slider('sharpness')

    def verify_slider(self, name):
        s = self.selenium
        selector = 'css=*[id="filter.%s"] .uislider' % name
        s.waitForElementPresent(selector)

        # Clicking 0 yields 0.75 as value and changes the image url
        image_url = s.getEval('window.document.imp.image.src')
        s.clickAt(selector, '0')
        s.verifyValue('filter.%s.input' % name, '-100')
        s.verifyEval(
            "window.document.imp.crop_arguments['filter.%s']" % name, '0.75')
        s.waitForEval(
            "window.document.imp.image.src == '%s'" % image_url, 'false')

        # Clicking > 0 increases the value:
        s.clickAt(selector, '100')
        s.verifyEval(
            "new Number(window.document.getElementById("
            "   'filter.%s.input').value) > -100" % name,
            'true')
        s.verifyEval(
            "window.document.imp.crop_arguments['filter.%s'] != 0" % name,
            'true')

        # clicking reset sets the slider back to 0 (filter becomes 1 then)
        s.click('reset')
        s.verifyEval(
            "window.document.imp.crop_arguments['filter.%s']" % name, '1')


class ContentZoomTest(Selenium):

    def test_zoom(self):
        s = self.selenium
        s.verifyElementNotPresent('css=#content.imp-zoomed-content')
        s.click('id=imp-content-zoom-toggle')
        s.verifyElementPresent('css=#content.imp-zoomed-content')
        s.click('id=imp-content-zoom-toggle')
        s.verifyElementNotPresent('css=#content.imp-zoomed-content')
