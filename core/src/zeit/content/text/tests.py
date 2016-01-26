import zeit.cms.testing


TextLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=zeit.cms.testing.cms_product_config)


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=TextLayer)
