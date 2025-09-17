import zeit.cms.testing
import zeit.content.gallery.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'entry-text.txt',
        'crop.txt',
        package='zeit.content.gallery.browser',
        layer=zeit.content.gallery.testing.WSGI_LAYER,
    )
