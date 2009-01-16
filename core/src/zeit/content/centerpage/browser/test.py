# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

import zeit.cms.testing
import zeit.content.centerpage.test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.centerpage.test.CenterPageLayer))
    return suite
