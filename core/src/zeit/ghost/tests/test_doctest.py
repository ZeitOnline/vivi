import zeit.cms.testing
import zeit.ghost.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', package='zeit.ghost', layer=zeit.ghost.testing.ZOPE_LAYER
    )
