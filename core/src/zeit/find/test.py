# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt


import unittest
import doctest

from zope.testing import doctest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE))
    return suite
