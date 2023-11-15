import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocFileSuite(
            'mock.txt', package='zeit.cms.workflow', optionflags=zeit.cms.testing.optionflags
        )
    )
    suite.addTest(
        zeit.cms.testing.FunctionalDocFileSuite(
            'modified.txt',
            'status.txt',
            package='zeit.cms.workflow',
        )
    )
    return suite
