# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.cms.testing
import zope.app.testing.functional


InfoboxLayer = zope.app.testing.functional.ZCMLLayer(
    pgk_resources.get_resourcefilename(__name__, 'ftesting.zcml'),
    __name__, 'InfoboxLayer', allow_teardown=True)




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=InfoboxLayer))
    return suite
