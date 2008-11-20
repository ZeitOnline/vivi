# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connector test setup."""

import os
import unittest
import zope.app.appsetup.product
import zope.app.testing.functional
import zope.file.testing
from zope.testing import doctest

import zeit.connector.cache


real_connector_layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ConnectorLayer', allow_teardown=True)


optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
             doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'connector.txt',
        'locking.txt',
        'mock.txt',
        optionflags=optionflags))

    long_running = doctest.DocFileSuite(
        'longrunning.txt',
        'stressing.txt',
        optionflags=optionflags)
    long_running.level = 3
    suite.addTest(long_running)

    functional = zope.file.testing.FunctionalBlobDocFileSuite(
        'functional.txt')
    functional.layer = real_connector_layer
    functional.level = 3
    suite.addTest(functional)

    cache = zope.file.testing.FunctionalBlobDocFileSuite(
        'cache.txt',
        optionflags=optionflags)
    cache.layer = real_connector_layer
    suite.addTest(cache)

    return suite


def print_tree(connector, base):
    """Helper to print a tree."""
    print '\n'.join(list_tree(connector, base))


def list_tree(connector, base, level=0):
    """Helper to print a tree."""
    result = []
    if level == 0:
        result.append(base)
    for name, uid in sorted(connector.listCollection(base)):
        result.append('%s %s' % (uid, connector[uid].type))
        if uid.endswith('/'):
            result.extend(list_tree(connector, uid, level+1))

    return result
