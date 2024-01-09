import unittest

import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.DocFileSuite('clip.txt', package='zeit.cms.clipboard.browser'))
    suite.addTest(
        zeit.cms.testing.FunctionalDocFileSuite('README.txt', package='zeit.cms.clipboard.browser')
    )
    return suite
