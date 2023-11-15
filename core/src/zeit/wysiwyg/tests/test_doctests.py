import zeit.cms.testing
import zeit.wysiwyg.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'html.txt', 'reference.txt', package='zeit.wysiwyg', layer=zeit.wysiwyg.testing.ZOPE_LAYER
    )
