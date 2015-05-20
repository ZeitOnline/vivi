from zeit.content.image.testing import create_image_group_with_master_image
import json
import zeit.cms.checkout.interfaces
import zeit.cms.testing
import zeit.content.image.testing


class VariantJsonAPI(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(VariantJsonAPI, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                group = create_image_group_with_master_image()
                self.group = zeit.cms.checkout.interfaces.ICheckoutManager(
                    group).checkout()
                self.group.variants = {
                    'square': {'focus_x': 0.5, 'focus_y': 0.5}
                }

    def test_list_variants(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/workingcopy/zope.user'
               '/group/variants')
        result = json.loads(b.contents)
        self.assertEqual(['default', 'cinema', 'square'],
                         [x['id'] for x in result])

    def test_get_variant(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/workingcopy/zope.user'
               '/group/variants/square')
        variant = json.loads(b.contents)
        self.assertEqual(0.5, variant['focus_x'])
