# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os

from zope.testing import doctest

import zope.component

import zope.app.testing.functional

import zeit.connector.interfaces


cms_layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CMSLayer', allow_teardown=True)


def FunctionalDocFileSuite(*paths, **kw):
    try:
        layer = kw['layer']
    except KeyError:
        layer = cms_layer
    else:
        del kw['layer']
    kw['package'] = doctest._normalize_module(kw.get('package'))

    def tearDown(test):
        zope.app.testing.functional.FunctionalTestSetup().tearDown()
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector._reset()
    kw['tearDown'] = tearDown

    test = zope.app.testing.functional.FunctionalDocFileSuite(
        *paths, **kw)
    test.layer = layer
    return test
