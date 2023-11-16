import zeit.cms.testing
import zeit.content.portraitbox.interfaces


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.content.portraitbox',
        layer=zeit.content.portraitbox.testing.ZOPE_LAYER,
    )
