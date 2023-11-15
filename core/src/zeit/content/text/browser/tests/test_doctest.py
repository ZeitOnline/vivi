import zeit.cms.testing
import zeit.content.text.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.content.text.browser',
        layer=zeit.content.text.testing.WSGI_LAYER,
    )
