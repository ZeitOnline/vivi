import zeit.cms.testing
import zeit.content.image.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.content.image',
        layer=zeit.content.image.testing.LAYER,
    )
