# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import re
import os
import unittest

import zope.app.testing.functional
from zope.testing import doctest


ObjectLogLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ObjectLogLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    test = zope.app.testing.functional.FunctionalDocFileSuite(
        'README.txt',
        optionflags=(doctest.INTERPRET_FOOTNOTES | doctest.ELLIPSIS |
                     doctest.REPORT_NDIFF | doctest.NORMALIZE_WHITESPACE))
    test.layer = ObjectLogLayer
    suite.addTest(test)
    return suite

