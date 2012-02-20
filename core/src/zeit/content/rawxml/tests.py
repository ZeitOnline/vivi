# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest
import zeit.cms.testing


RawXMLLayer = zeit.cms.testing.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'RawXMLLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=RawXMLLayer))
    return suite
