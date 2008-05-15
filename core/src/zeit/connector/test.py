# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

import zope.file.testing
from zope.testing import doctest

import zope.app.testing.functional
import zope.app.appsetup.product

import zeit.connector.cache


real_connector_layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ConnectorLayer')


def tearDown(test):
    zeit.connector.cache._cleanup()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'connector.txt',
        'mock.txt',
        'cache.txt',
        'locking.txt',
        tearDown=tearDown,
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES)))
    functional = zope.file.testing.FunctionalBlobDocFileSuite(
        'functional.txt')
    functional.layer = real_connector_layer
    suite.addTest(functional)
    return suite


def print_tree(connector, base, level=0):
    """Helper to print a tree."""
    if level == 0:
        print base
    for name, uid in sorted(connector.listCollection(base)):
        print uid, connector[uid].type
        if uid.endswith('/'):
            print_tree(connector, uid, level+1)
