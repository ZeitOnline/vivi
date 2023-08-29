import zeit.cms.testing
import zeit.content.rawxml.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.rawxml.testing.WSGI_LAYER,
        package='zeit.content.rawxml.browser')
