# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

import zope.app.testing.functional
import zope.app.appsetup.product
from zope.testing import doctest

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
        tearDown=tearDown,
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS)))
    functional = zope.app.testing.functional.FunctionalDocFileSuite(
        'functional.txt')
    functional.layer = real_connector_layer
    suite.addTest(functional)
    return suite
