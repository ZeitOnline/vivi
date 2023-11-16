import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('content.txt', package='zeit.cms'))
    suite.addTest(
        zeit.cms.testing.FunctionalDocFileSuite('cleanup.txt', 'cmscontent.txt', package='zeit.cms')
    )
    return suite
