# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.cms.testing
import zope.app.testing.functional


layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'zeit.content.cp.tests.layer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=layer))
    return suite
