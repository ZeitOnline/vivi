# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import re
import os
import unittest

import zope.testing.renormalizing
from zope.testing import doctest

import zope.app.testing.functional


ObjectLogLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ObjectLogLayer', allow_teardown=True)


FORMATTED_DATE_REGEX = re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d')
checker = zope.testing.renormalizing.RENormalizing([
    (FORMATTED_DATE_REGEX, '<formatted date>')])


def test_suite():
    suite = unittest.TestSuite()
    test = zope.app.testing.functional.FunctionalDocFileSuite(
        'README.txt',
        optionflags=(doctest.INTERPRET_FOOTNOTES | doctest.ELLIPSIS |
                     doctest.REPORT_NDIFF | doctest.NORMALIZE_WHITESPACE),
        checker=checker)
    test.layer = ObjectLogLayer
    suite.addTest(test)
    return suite

