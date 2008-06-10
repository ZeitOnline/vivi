# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing


WorkflowLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'WorkflowLayer', allow_teardown=True)


product_config = {
    'publish-script': os.path.join(
        os.path.dirname(__file__), 'publish.sh'),
    'retract-script': 'XXX',
    'path-prefix': 'work',
}

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'syndication.txt',
        layer=WorkflowLayer,
        product_config={'zeit.workflow': product_config},
        optionflags=(doctest.INTERPRET_FOOTNOTES|doctest.ELLIPSIS|
                     doctest.REPORT_NDIFF|doctest.NORMALIZE_WHITESPACE)))
    return suite
