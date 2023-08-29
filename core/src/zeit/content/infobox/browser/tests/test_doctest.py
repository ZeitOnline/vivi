import zeit.cms.testing
import zeit.content.infobox.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.content.infobox.browser',
        layer=zeit.content.infobox.testing.WSGI_LAYER)
