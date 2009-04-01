# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing
import zeit.content.cp.tests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        checker=zeit.content.cp.tests.checker,
        layer=zeit.content.cp.tests.layer))
    return suite
