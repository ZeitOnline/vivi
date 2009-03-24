# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.cp.test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.content.cp.test.layer))
    return suite
