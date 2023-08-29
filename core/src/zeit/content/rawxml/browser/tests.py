import zeit.cms.testing
import zeit.content.rawxml.tests


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.rawxml.tests.WSGI_LAYER)
