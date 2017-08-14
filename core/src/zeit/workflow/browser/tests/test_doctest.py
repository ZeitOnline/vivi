import unittest
import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'indicator.txt',
        package='zeit.workflow.browser',
        layer=zeit.workflow.testing.CELERY_LAYER))
    return suite
