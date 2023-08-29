import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'recension.txt',
        package='zeit.content.article',
        layer=zeit.content.article.testing.LAYER)
