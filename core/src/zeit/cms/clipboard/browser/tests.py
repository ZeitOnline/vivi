# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.DocFileSuite('clip.txt'))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt'))
    return suite
