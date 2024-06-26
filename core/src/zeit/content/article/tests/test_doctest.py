import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'recension.txt',
        package='zeit.content.article',
        layer=zeit.content.article.testing.LAYER,
    )
