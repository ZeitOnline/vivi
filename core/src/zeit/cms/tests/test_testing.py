# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2 as unittest
import zeit.cms.testing


class TestProductConfigIsolation(zeit.cms.testing.FunctionalTestCase):

    def test_1_set_product_config(self):
        import zope.app.appsetup.product
        zope.app.appsetup.product._configs['zeit.cms'][
            'isolated'] = 'i-am-isolated'

    def test_2_second_test_should_not_see_changes_from_first_test(self):
        import zope.app.appsetup.product
        self.assertNotIn(
            'isolated', zope.app.appsetup.product._configs['zeit.cms'])


class LayerWithProductConfig(zeit.cms.testing.cms_layer):

    @classmethod
    def testSetUp(cls):
        import zope.app.appsetup.product
        zope.app.appsetup.product._configs['zeit.foo'] = {}
        product_config = zope.app.appsetup.product._configs['zeit.foo']
        product_config['available'] = 'in-test'

    @classmethod
    def testTearDown(cls):
        pass

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'test_testing_isolation.txt',
        layer = LayerWithProductConfig))
    suite.addTest(unittest.makeSuite(TestProductConfigIsolation))
    return suite


