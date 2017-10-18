import unittest
import zeit.content.cp
import zeit.content.cp.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'README.txt',
        'cmscontentiterable.txt',
        'rule.txt',
        package=zeit.content.cp))
    return suite
