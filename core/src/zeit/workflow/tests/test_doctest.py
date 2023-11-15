import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', layer=zeit.workflow.testing.CELERY_LAYER, package='zeit.workflow'
    )
