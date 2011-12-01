# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import re
import unittest

import zope.testing.renormalizing
from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d'), '<FORMATTED DATE>')
])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES),
        checker=checker))
    return suite
