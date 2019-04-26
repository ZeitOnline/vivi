import unittest
import zeit.cms.testing
import zeit.content.rawxml.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.rawxml.tests.RawXMLLayer))
    return suite
