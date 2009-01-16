# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing

import zeit.content.portraitbox.test

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        optionflags=(doctest.INTERPRET_FOOTNOTES + doctest.NORMALIZE_WHITESPACE
                    + doctest.ELLIPSIS + doctest.REPORT_NDIFF),
        layer=zeit.content.portraitbox.test.PortraitboxLayer))
    return suite
