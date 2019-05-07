import unittest
import zeit.cms.testing


SEOLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=zeit.cms.testing.cms_product_config)
WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(SEOLayer,))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=WSGI_LAYER))
    return suite
