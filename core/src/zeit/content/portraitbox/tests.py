# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import pkg_resources
import unittest
import zeit.cms.testing
import zope.app.testing.functional


PortraitboxLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'PortraitboxLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=PortraitboxLayer))
    return suite
