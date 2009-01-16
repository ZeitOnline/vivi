# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

import zope.app.testing.functional
from zope.testing import doctest

import zeit.cms.testing


ConnectorProfilingLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'profiling.zcml'),
    __name__, 'ConnectorProfilingLayer', allow_teardown=True)


def connectorFactory():
    import zeit.connector.connector
    return zeit.connector.connector.Connector(
        dict(default='http://zip6.zeit.de/cms/work/'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'full-profiling.txt',
        layer=ConnectorProfilingLayer))
    return suite
