import zeit.cms.testing
import zeit.content.link.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.link.testing.ZCML_LAYER)
