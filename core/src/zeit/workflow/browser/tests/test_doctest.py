import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'indicator.txt',
        package='zeit.workflow.browser',
        layer=zeit.workflow.testing.WSGI_LAYER,
    )
