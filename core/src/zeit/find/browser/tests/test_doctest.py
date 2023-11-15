import zeit.cms.testing
import zeit.find.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', package='zeit.find.browser', layer=zeit.find.testing.WSGI_LAYER
    )
