import unittest
import zeit.cms.testing


SEOLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=zeit.cms.testing.cms_product_config)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=SEOLayer))
    return suite
