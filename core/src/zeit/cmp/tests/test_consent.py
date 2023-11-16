from zeit.cms.checkout.helper import checked_out
import zeit.cmp.interfaces
import zeit.cmp.testing


class ConsentInfo(zeit.cmp.testing.FunctionalTestCase):
    def test_stores_values_in_dav(self):
        with checked_out(self.repository['testcontent']) as co:
            info = zeit.cmp.interfaces.IConsentInfo(co)
            info.has_thirdparty = True
            info.thirdparty_vendors = ['twitter', 'facebook']

        info = zeit.cmp.interfaces.IConsentInfo(self.repository['testcontent'])
        self.assertEqual(True, info.has_thirdparty)
        self.assertEqual(('twitter', 'facebook'), info.thirdparty_vendors)
        self.assertEqual(('cmp-twitter', 'cmp-facebook'), info.thirdparty_vendors_cmp_ids)
