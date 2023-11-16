import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', package='zeit.workflow.xmlrpc', layer=zeit.workflow.testing.WSGI_LAYER
    )
