import zeit.cms.testing
import zeit.objectlog.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', package='zeit.objectlog', layer=zeit.objectlog.testing.ZOPE_LAYER
    )
