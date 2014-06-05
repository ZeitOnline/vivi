# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.testing


GhostLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=GhostLayer))
    return suite
