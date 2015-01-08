import zeit.cms.testing


RawXMLLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=RawXMLLayer)
