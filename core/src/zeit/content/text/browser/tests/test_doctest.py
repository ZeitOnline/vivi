import unittest
import zeit.cms.testing
import zeit.content.text.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.content.text.browser',
        layer=zeit.content.text.testing.ZCML_LAYER))
    return suite
