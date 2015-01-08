import zeit.cms.testing


TextLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=TextLayer)
