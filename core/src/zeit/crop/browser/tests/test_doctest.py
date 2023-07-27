import zeit.cms.testing
import zeit.crop.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.crop.browser',
        layer=zeit.crop.testing.WSGI_LAYER)
