# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


CalendarLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CalendarLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'README.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS)))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'calendar.txt',
        layer=CalendarLayer))
    return suite
