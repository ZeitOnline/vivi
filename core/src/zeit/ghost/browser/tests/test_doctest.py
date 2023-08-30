import zeit.cms.testing
import zeit.ghost.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'checkin.txt',
        layer=zeit.ghost.testing.WSGI_LAYER,
        package='zeit.ghost.browser')
