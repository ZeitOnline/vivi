import zeit.cms.testing
import zeit.content.image.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'transform.txt',
        'masterimage.txt',
        package='zeit.content.image',
        layer=zeit.content.image.testing.ZOPE_LAYER)
