import zeit.cms.testing
import zeit.content.rawxml.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.content.rawxml',
        layer=zeit.content.rawxml.testing.ZOPE_LAYER)
