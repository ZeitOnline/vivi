import zeit.cms.testing
import zeit.invalidate.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', package='zeit.invalidate', layer=zeit.invalidate.testing.WSGI_LAYER
    )
