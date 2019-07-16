import zeit.cms.testing
import zeit.purge.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.purge.testing.WSGI_LAYER)
