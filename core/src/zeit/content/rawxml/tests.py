import zeit.cms.testing


RawXMLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=zeit.cms.testing.cms_product_config)

WSGI_LAYER = zeit.cms.testing.WSGILayer(
    name='WSGILayer', bases=(RawXMLLayer,))


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=RawXMLLayer)
