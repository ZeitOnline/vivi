from zeit.content.image.testing import create_image_group_with_master_image
import gocept.jasmine.jasmine
import json
import requests
import transaction
import zeit.cms.checkout.interfaces
import zeit.cms.testing
import zeit.content.image.testing


class VariantJsonAPI(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.HTTP_LAYER

    def setUp(self):
        super(VariantJsonAPI, self).setUp()
        group = create_image_group_with_master_image()
        self.group = zeit.cms.checkout.interfaces.ICheckoutManager(
            group).checkout()
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

    def test_list_variants(self):
        r = self.request('get', '/workingcopy/zope.user/group/variants')
        self.assertEqual(['default', 'cinema', 'square'],
                         [x['id'] for x in r.json()])

    def test_get_variant(self):
        r = self.request('get', '/workingcopy/zope.user/group/variants/square')
        variant = r.json()
        self.assertEqual(0.5, variant['focus_x'])

    def test_put_variant_stores_values(self):
        self.request('put', '/workingcopy/zope.user/group/variants/square',
                     data=json.dumps({'focus_x': 0.1, 'focus_y': 0.1}))
        transaction.abort()
        self.assertEqual(0.1, self.group.variants['square']['focus_x'])


class VariantApp(gocept.jasmine.jasmine.TestApp):

    def need_resources(self):
        zeit.content.image.browser.resources.test_variant_js.need()


class VariantJasmineTestCase(gocept.jasmine.jasmine.TestCase):

    layer = gocept.jasmine.jasmine.get_layer(VariantApp())
    level = 2

    def test_all_jasmine_unit_tests_run_successfully(self):
        self.run_jasmine()
