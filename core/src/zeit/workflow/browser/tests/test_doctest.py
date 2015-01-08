import unittest
import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'indicator.txt',
        'nagios.txt',
        package='zeit.workflow.browser',
        layer=zeit.workflow.testing.LAYER))
    return suite
