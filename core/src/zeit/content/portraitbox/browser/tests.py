import unittest
import zeit.cms.testing
import zeit.content.portraitbox.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.portraitbox.tests.PortraitboxLayer))
    return suite
