# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import unittest
import zeit.cms.testing
import zope.app.testing.functional


layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'zeit.content.cp.tests.layer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=layer))
    return suite
