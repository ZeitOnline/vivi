# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        '../badge.txt'))
    return suite
