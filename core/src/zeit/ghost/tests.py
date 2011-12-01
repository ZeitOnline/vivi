# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


GhostLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'GhostLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=GhostLayer))
    return suite
