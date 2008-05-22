# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import re
import os
import unittest

import zope.app.testing.functional
from zope.testing import doctest

import zeit.cms.testing


RelationLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'RelationLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        optionflags=(doctest.INTERPRET_FOOTNOTES | doctest.ELLIPSIS |
                     doctest.REPORT_NDIFF | doctest.NORMALIZE_WHITESPACE),
        layer=RelationLayer))
    return suite
