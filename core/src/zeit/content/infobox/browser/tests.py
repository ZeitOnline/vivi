import unittest
import zeit.cms.testing
import zeit.content.infobox.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.infobox.tests.InfoboxLayer))
    return suite
