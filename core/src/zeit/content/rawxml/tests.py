# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest

import zope.app.testing.functional

import zeit.cms.testing


RawXMLLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'RawXMLLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=RawXMLLayer))
    return suite
