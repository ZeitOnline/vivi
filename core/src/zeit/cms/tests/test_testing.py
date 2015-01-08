import plone.testing
import unittest
import zeit.cms.testing


class TestProductConfigIsolation(zeit.cms.testing.ZeitCmsTestCase):

    def test_1_set_product_config(self):
        import zope.app.appsetup.product
        zope.app.appsetup.product._configs['zeit.cms'][
            'isolated'] = 'i-am-isolated'

    def test_2_second_test_should_not_see_changes_from_first_test(self):
        import zope.app.appsetup.product
        self.assertNotIn(
            'isolated', zope.app.appsetup.product._configs['zeit.cms'])


class LayerWithProductConfig(plone.testing.Layer):

    defaultBases = (zeit.cms.testing.ZCML_LAYER,)

    def testSetUp(self):
        import zope.app.appsetup.product
        zope.app.appsetup.product._configs['zeit.foo'] = {}
        product_config = zope.app.appsetup.product._configs['zeit.foo']
        product_config['available'] = 'in-test'

PRODUCT_CONFIG_LAYER = LayerWithProductConfig()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'test_testing_isolation.txt',
        layer=PRODUCT_CONFIG_LAYER))
    suite.addTest(unittest.makeSuite(TestProductConfigIsolation))
    return suite
