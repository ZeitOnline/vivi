import zeit.cms.testing
import zeit.content.portraitbox.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.content.portraitbox.browser',
        layer=zeit.content.portraitbox.testing.WSGI_LAYER)
