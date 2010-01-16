# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import unittest

import zope.app.testing.functional

import zeit.cms.testing


CenterPageLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CenterPageLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=CenterPageLayer))
    return suite
