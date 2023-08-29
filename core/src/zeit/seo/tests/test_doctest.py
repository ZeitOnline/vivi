import zeit.cms.testing
import zeit.seo.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.seo',
        layer=zeit.seo.testing.WSGI_LAYER)
