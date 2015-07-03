from zeit.content.image.testing import create_image_group_with_master_image
import gocept.jasmine.jasmine
import json
import requests
import transaction
import unittest
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.interfaces
import zeit.content.image.testing
import zope.component


class VariantJsonAPI(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.HTTP_LAYER

    def setUp(self):
        super(VariantJsonAPI, self).setUp()
        self.group = create_image_group_with_master_image()
        self.group.variants = {
            'square': {'focus_x': 0.5, 'focus_y': 0.5}
        }
        transaction.commit()

    def request(self, method, path, **kw):
        response = getattr(requests, method)('http://%s/++skin++vivi%s' % (
            self.layer['http_address'], path), auth=('user', 'userpw'), **kw)
        if response.status_code >= 400:
            raise ValueError('HTTP status %s:\n%s' % (
                response.status_code, response.text))
        return response

    def test_list_variants_excludes_default(self):
        r = self.request('get', '/repository/group/variants')
        self.assertEqual(['cinema-small', 'cinema-large', 'square'],
                         [x['id'] for x in r.json()])

    def test_get_variant_contains_all_fields_defined_on_interface_and_url(
            self):
        r = self.request('get', '/repository/group/variants/square')
        variant = r.json()
        self.assertEqual(0.5, variant['focus_x'])
        self.assertEqual(0.5, variant['focus_y'])
        self.assertEqual(
            sorted(['url'] + list(zeit.content.image.interfaces.IVariant)),
            sorted(variant.keys()))

    def test_put_variant_stores_focuspoint_and_zoom_only(self):
        # All other attributes are transient or come from XML
        fields = zope.schema.getFields(zeit.content.image.interfaces.IVariant)
        data = {}
        for key in fields.keys():
            data[key] = 1

        self.request(
            'put', '/repository/group/variants/square', data=json.dumps(data))
        transaction.abort()
        self.assertEqual(
            ['focus_x', 'focus_y', 'zoom'],
            sorted(self.group.variants['square'].keys()))

    def test_put_variant_stores_value_of_focuspoint_and_zoom(self):
        self.request(
            'put', '/repository/group/variants/square',
            data=json.dumps({'focus_x': 0.1, 'focus_y': 0.2, 'zoom': 1.0}))
        transaction.abort()
        self.assertEqual(
            {'focus_x': 0.1, 'focus_y': 0.2, 'zoom': 1.0},
            self.group.variants['square'])

    def test_put_variant_returns_error_if_focuspoint_was_set_to_None(self):
        # Setting focuspoint to None would break Image generation
        with self.assertRaises(ValueError):
            self.request(
                'put', '/repository/group/variants/square',
                data=json.dumps({'focus_x': None, 'focus_y': None}))
        transaction.abort()
        self.assertEqual(
            {'focus_x': 0.5, 'focus_y': 0.5}, self.group.variants['square'])

    def test_put_variant_returns_error_if_zoom_was_set_to_None(self):
        # Setting zoom to None would break Image generation
        with self.assertRaises(ValueError):
            self.request(
                'put', '/repository/group/variants/square',
                data=json.dumps({'zoom': None}))
        transaction.abort()
        self.assertEqual(
            {'focus_x': 0.5, 'focus_y': 0.5}, self.group.variants['square'])

    def test_delete_removes_variant_config_from_group(self):
        self.request('delete', '/repository/group/variants/square')
        self.assertEqual({}, self.group.variants)

    def test_delete_for_variant_without_config_succeeds_anyway(self):
        with self.assertNothingRaised():
            self.request('delete', '/repository/group/variants/cinema-small')


class VariantIntegrationTest(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.content.image.testing.WEBDRIVER_LAYER
    window_width = 1400  # The "Variants" tab needs to fit in and be clickable.

    def test_integration(self):
        """Open Image group and change settings of master and a variant."""
        s = self.selenium
        self.open('/repository/2007/03/group')
        s.click('link=Variants')
        s.waitForCssCount('css=#variant-content', 1)  # wait for tab to load

        # test that descriptive name is displayed near image
        s.assertTextPresent('Vollbreit (L)')

        # change default
        s.dragAndDrop('css=.ui-slider-handle', '0,-50')
        s.dragAndDrop('css=.focuspoint', '50,50')
        s.waitForCssCount('css=.saved', 1)
        s.waitForCssCount('css=.saved', 0)

        # switch to first preview, i.e. cinema-small
        s.click('css=img.preview')
        s.waitForCssCount('css=.switched', 1)
        s.waitForCssCount('css=.switched', 0)

        # change settings for cinema-small
        s.dragAndDrop('css=.cropper-point.point-nw', '50,50')
        s.waitForCssCount('css=.saved', 1)
        s.waitForCssCount('css=.saved', 0)

        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        variants = repository['2007']['03']['group'].variants
        self.assertEqual(['cinema-small', 'default'], sorted(variants.keys()))
        # Compare Zoom values: cinema-small < default < 1 (default setting)
        self.assertLess(variants['default']['zoom'], 1)
        self.assertLess(
            variants['cinema-small']['zoom'],
            variants['default']['zoom'])
        # Compare Focus Point: cinema-small > default > 0.5 (default setting)
        self.assertGreater(variants['default']['focus_x'], 0.5)
        self.assertGreater(
            variants['cinema-small']['focus_x'],
            variants['default']['focus_x'])

        s.click('css=input[value=Verwerfen]')
        s.waitForCssCount('css=.reset_single', 1)
        s.waitForCssCount('css=.reset_single', 0)

        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        variants = repository['2007']['03']['group'].variants
        self.assertEqual(['default'], sorted(variants.keys()))


class VariantApp(gocept.jasmine.jasmine.TestApp):

    def need_resources(self):
        zeit.content.image.browser.resources.test_variant_js.need()


class VariantJasmineTestCase(gocept.jasmine.jasmine.TestCase):

    layer = gocept.jasmine.jasmine.get_layer(VariantApp())
    level = 2

    def test_all_jasmine_unit_tests_run_successfully(self):
        self.run_jasmine()
