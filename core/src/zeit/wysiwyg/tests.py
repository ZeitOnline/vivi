# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.cms.testing
import zope.app.testing.functional


WYSIWYGLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'WYSIWYGLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'html.txt',
        layer=WYSIWYGLayer))
    return suite
