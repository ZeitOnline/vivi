import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'edit.landing.txt',
        'edit.txt',
        'edit.form.txt',
        package='zeit.content.article.edit.browser',
        layer=zeit.content.article.testing.WSGI_LAYER,
    )
