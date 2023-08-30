import zeit.cms.testing
import zeit.content.gallery.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'reference.txt',
        package='zeit.content.gallery',
        layer=zeit.content.gallery.testing.ZOPE_LAYER)
