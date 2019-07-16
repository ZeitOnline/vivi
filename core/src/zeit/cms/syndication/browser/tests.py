import doctest
import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt'))
    suite.addTest(doctest.DocFileSuite(
        'feed.txt', optionflags=zeit.cms.testing.optionflags))
    return suite
