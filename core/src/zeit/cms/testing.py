# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os

from zope.testing import doctest

import zope.app.testing.functional


CMSLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CMSLayer', allow_teardown=True)


def FunctionalDocFileSuite(*paths, **kw):
    try:
        layer = kw['layer']
    except KeyError:
        layer = CMSLayer
    else:
        del kw['layer']
    kw['package'] = doctest._normalize_module(kw.get('package'))
    test = zope.app.testing.functional.FunctionalDocFileSuite(
        *paths, **kw)
    test.layer = layer
    return test
