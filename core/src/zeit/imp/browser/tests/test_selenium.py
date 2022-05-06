# coding: utf8
from selenium.webdriver.common.keys import Keys
import gocept.selenium
import unittest
import zeit.cms.testing
import zeit.content.image.testing
import zeit.imp.tests


WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(zeit.imp.tests.ZOPE_LAYER,))
HTTP_LAYER = zeit.cms.testing.WSGIServerLayer(
    name='HTTPLayer', bases=(WSGI_LAYER,))
WD_LAYER = zeit.cms.testing.WebdriverLayer(
    name='WebdriverLayer', bases=(HTTP_LAYER,))
WEBDRIVER_LAYER = gocept.selenium.WebdriverSeleneseLayer(
    name='WebdriverSeleneseLayer', bases=(WD_LAYER,))


class Selenium(zeit.cms.testing.SeleniumTestCase):

    layer = WEBDRIVER_LAYER
    window_width = 1100
    window_height = 600

    def setUp(self):
        super().setUp()
        self.create_group()
        self.open_imp()

    def create_group(self):
        zeit.content.image.testing.create_image_group_with_master_image()

    def open_imp(self):
        self.open('/repository/group/@@imp.html')


class SeleniumBasicTests(Selenium):

    def test_generic_load(self):
        self.selenium.assertTextPresent('450×200')

    def test_crop_mask(self):
        s = self.selenium

        # s.comment('After clicking on the mask choice the image is loaded')
        self.click_label('450×200')
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=')

        # s.comment('The border will be passed')
        self.click_label("grauer Rahmen")
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=%23888888')

    def test_border_select_wo_selected_mask_does_not_fail(self):
        s = self.selenium

        self.click_label("schwarzer Rahmen")
        s.verifyElementNotPresent('id=imp-mask-image')
        self.click_label('450×200')
        s.verifyAttribute(
            'id=imp-mask-image@src',
            '*&mask_width=450&mask_height=200&border=%23000000')

    def test_image_dragging(self):
        s = self.selenium
        pos = self.eval('window.document.imp.get_image_position()')
        self.assertEqual(1, pos['x'])
        self.assertEqual(1, pos['y'])
        s.pause(500)  # XXX What should we be waiting for here?
        s.dragAndDrop('id=imp-mask', '30,100')
        pos = self.eval('window.document.imp.get_image_position()')
        self.assertEqual(31, pos['x'])
        self.assertEqual(101, pos['y'])

    def test_mask_string_parse(self):
        s = self.selenium

        # s.comment('Simple dimensions')
        s.runScript(
            'window.document.imp.set_mask("500x200/500/200")')
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.name', '"500x200"')

        # s.comment('The dimensions can be variable, indicated by a ?')
        s.runScript(
            'window.document.imp.set_mask("art-200/?500/200")')
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.mask_variable.w', 'true')
        s.verifyEval('window.document.imp.mask_variable.h', 'false')
        s.verifyEval('window.document.imp.name', '"art-200"')

        s.runScript('window.document.imp.set_mask("foo/?500/?200")')
        s.verifyEval('window.document.imp.mask_dimensions.w', '500')
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.verifyEval('window.document.imp.mask_variable.w', 'true')
        s.verifyEval('window.document.imp.mask_variable.h', 'true')
        s.verifyEval('window.document.imp.name', '"foo"')

    def test_zoom_slider(self):
        s = self.selenium
        # s.comment('Zooming works with a slider')
        s.verifyEval('window.document.imp.zoom>1', 'false')
        s.clickAt('id=imp-zoom-slider', '500,0')
        s.waitForEval('window.document.imp.zoom>1', 'true')

    def test_zoom_mouse_wheel(self):
        zoom = float(self.eval('window.document.imp.zoom.toPrecision(3)'))
        self.zoom_with_wheel(10000)
        self.assertGreater(self.eval('window.document.imp.zoom'), 1)
        self.zoom_with_wheel(-9000)
        self.assertLess(self.eval('window.document.imp.zoom'), 1)
        self.assertGreater(self.eval('window.document.imp.zoom'), zoom)

    def test_zoom_with_mouse_wheel_updates_slider(self):
        s = self.selenium
        s.verifyEval('window.document.imp_zoom_slider.get_value()>1', 'false')
        self.zoom_with_wheel(10000)
        s.verifyEval('window.document.imp_zoom_slider.get_value()>1', 'true')

    def zoom_with_wheel(self, delta_y):
        self.selenium.runScript("""\
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
        # s.comment('Nothing happens when the crop button is clicked.')
        s.click('id=imp-action-crop')
        s.verifyElementNotPresent('css=#imp-image-bar > div')

    def test_crop(self):
        s = self.selenium
        s.verifyElementNotPresent('css=#imp-image-bar > div')
        s.verifyElementNotPresent('css=label.cropped')
        s.dragAndDrop('id=imp-mask', '-30,-100')
        self.click_label('450×200')
        s.click('id=imp-action-crop')
        # s.comment('After cropping the image is inserted in the image bar')
        s.waitForElementPresent('css=#imp-image-bar > div')
        # s.comment('The label is marked as "cropped"')
        s.verifyElementPresent('css=label.cropped')

    def test_crop_outside_mask(self):
        # Since VIV-500 we need to trouble ourselves a bit to produce such a
        # scenario: Zoom in, drag it off-center, zoom out again. As the center
        # is somewhat preserved by zooming operations, the image will be moved
        # outside the mask afterwards.
        s = self.selenium
        s.verifyElementNotPresent('css=#imp-image-bar > div')
        s.verifyElementNotPresent('css=label.cropped')
        self.click_label('140×140')
        s.clickAt('id=imp-zoom-slider', '500,0')
        s.setWindowSize(self.window_width, 1000)
        s.dragAndDrop('id=imp-mask', '+500,+500')
        s.clickAt('id=imp-zoom-slider', '1,0')
        s.click('id=imp-action-crop')
        s.verifyAlert('Das Bild ist nicht*')
        s.verifyElementNotPresent('css=#imp-image-bar > div')

    @unittest.skip(
        'selenium3 does not support dragging beyond the window boundaries')
    def test_drag_outside_mask_snaps_to_mask(self):
        # As it snaps to the mask we can crop the image and no alert is
        # generated.
        s = self.selenium
        self.click_label('450×200')
        s.dragAndDrop('id=imp-mask', '+1000,+1000')
        s.click('id=imp-action-crop')
        s.waitForElementPresent('css=#imp-image-bar > div')

    def test_zoom_slider_has_minimum_of_mask_size(self):
        s = self.selenium
        # Put the zoom slider somewhere else than the minimum,
        self.click_label('450×200')
        s.clickAt('id=imp-zoom-slider', '500,0')
        # then select another mask
        self.click_label('140×140')
        # Assert that the slider is at the minimum value
        self.wait_for_condition(
            'window.jQuery("#imp-zoom-slider div").position().left == 0')
        zoom = self.eval('document.imp_zoom_slider.get_value()')
        self.assertTrue(str(zoom).startswith('0.09'))


class SeleniumMaskTests(Selenium):

    def test_input_fields_show_mask_size(self):
        s = self.selenium
        self.click_label('450×200')
        s.verifyValue('mask-w', '450')
        s.verifyValue('mask-h', '200')
        self.click_label('210×210')
        s.verifyValue('mask-w', '210')
        s.verifyValue('mask-h', '210')

    def test_input_fields_disabled_for_fixed_mask(self):
        s = self.selenium
        self.click_label('450×200')
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
        for i in range(3):
            s.keyPress('mask-h', Keys.BACKSPACE)
        s.type('name=mask-h', '280')
        s.keyPress('mask-h', Keys.RETURN)
        s.verifyEval('window.document.imp.mask_dimensions.h', '280')

    def test_input_field_up_arrow_once_increases_by_1(self):
        self.verify_press(Keys.ARROW_UP, '201')

    def test_input_field_down_arrow_once_decreases_by_1(self):
        self.verify_press(Keys.ARROW_DOWN, '199')

    def test_input_field_left_arrow_once_decreases_by_1(self):
        self.verify_press(Keys.ARROW_LEFT, '199')

    def test_input_field_right_arrow_once_increases_by_1(self):
        self.verify_press(Keys.ARROW_RIGHT, '201')

    def verify_press(self, key_code, expected_value):
        s = self.selenium
        self.click_label("Artikelbild breit")
        s.verifyEval('window.document.imp.mask_dimensions.h', '200')
        s.keyPress('mask-h', key_code)
        s.verifyEval('window.document.imp.mask_dimensions.h', expected_value)

    @unittest.skip('python webdriver bindings cannot hold down keys')
    def test_input_field_up_arrow_hold_increases(self):
        self.verify_hold(Keys.ARROW_UP, '>210')

    @unittest.skip('python webdriver bindings cannot hold down keys')
    def test_input_field_down_arrow_hold_decreases(self):
        self.verify_hold(Keys.ARROW_DOWN, '<190')

    @unittest.skip('python webdriver bindings cannot hold down keys')
    def test_input_field_left_arrow_hold_decreases(self):
        self.verify_hold(Keys.ARROW_LEFT, '<190')

    @unittest.skip('python webdriver bindings cannot hold down keys')
    def test_input_field_right_arrow_hold_increases(self):
        self.verify_hold(Keys.ARROW_RIGHT, '>210')

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
        y1 = s.getEval('window.document.imp.get_crop_arguments().y1')
        y2 = s.getEval('window.document.imp.get_crop_arguments().y2')
        self.assertIn(y1, ('53', '54'))  # Rounding issues
        self.assertIn(y2, ('253', '254'))  # Rounding issues

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
        super().setUp()
        # Choose a mask
        self.click_label('450×200')

    def test_window_resize_updates_mask(self):
        s = self.selenium
        # Store the current mask image dimensions
        width = int(s.getEval('window.document.imp.mask_image_dimensions.w'))
        height = int(s.getEval('window.document.imp.mask_image_dimensions.h'))
        # Increase the window width affects mask, try width only first:
        s.setWindowSize(1200, 800)
        s.waitForEval(
            "window.document.imp.mask_image_dimensions.w > %d" % width,
            'true')
        self.assertEqual(
            height,
            int(s.getEval("window.document.imp.mask_image_dimensions.h")))

        # change width and height:
        s.setWindowSize(800, 900)
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
        crop_args = self.eval(get_crop_args)

        s.setWindowSize(900, 900)
        s.pause(500)
        self.assertEqual(crop_args, self.eval(get_crop_args))

        # Try another one, to be sure this works multiple times
        s.setWindowSize(1000, 800)
        s.pause(500)
        self.assertEqual(crop_args, self.eval(get_crop_args))

    def test_window_resize_updates_zoom_slider(self):
        # The zoom slider doesn't automatically support size updates.
        s = self.selenium
        max_left = s.getEval(
            'window.document.imp_zoom_slider.zoom_slider._maxLeft')
        s.setWindowSize(800, 900)
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
        self.eval(
            'document.querySelector(\'%s\').scrollIntoView()' %
            selector.replace('css=', ''))

        # Clicking 0 yields 0.75 as value and changes the image url
        image_url = s.getEval('window.document.imp.image.src')
        s.clickAt(selector, '1,5')
        s.verifyValue('filter.%s.input' % name, '-100')
        s.verifyEval(
            "window.document.imp.crop_arguments['filter.%s']" % name, '0.75')
        s.waitForEval(
            "window.document.imp.image.src == '%s'" % image_url, 'false')

        # Clicking > 0 increases the value:
        s.clickAt(selector, '100,5')
        s.verifyEval(
            "new Number(window.document.getElementById("
            "   'filter.%s.input').value) > -100" % name,
            'true')
        s.verifyEval(
            "window.document.imp.crop_arguments['filter.%s'] != 0" % name,
            'true')

        # clicking reset sets the slider back to 0 (filter becomes 1 then)
        s.click('id=imp-action-reset')
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
