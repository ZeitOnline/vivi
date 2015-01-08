
import unittest
import zeit.cms.testing
import zeit.content.text.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.text.tests.TextLayer))
    return suite
