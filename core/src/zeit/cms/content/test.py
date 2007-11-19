# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import unittest

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'adapter.txt',
        'keyword.txt',
        'property.txt',
        'sources.txt',
        'locking.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS)))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite('dav.txt'))
    return suite
