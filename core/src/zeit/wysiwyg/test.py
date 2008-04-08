# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import re
import os
import unittest

import zope.testing.renormalizing
from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


WYSIWYGLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'WYSIWYGLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'html.txt',
        layer=WYSIWYGLayer))
    return suite
