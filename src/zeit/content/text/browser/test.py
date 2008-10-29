# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Text browser test setup."""

import unittest

import zeit.cms.testing
import zeit.content.text.test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.text.test.TextLayer))
    return suite
