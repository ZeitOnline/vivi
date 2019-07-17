import zeit.cms.testing
import zeit.imp.tests


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.imp.browser',
        layer=zeit.imp.tests.WSGI_LAYER)
