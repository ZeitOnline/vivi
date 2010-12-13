# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.portraitbox.interfaces
import zope.app.testing.functional


PortraitboxLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'PortraitboxLayer', allow_teardown=True)


class PortraitboxSourceTest(
    zeit.cms.content.tests.test_contentsource.ContentSourceTest):

    layer = PortraitboxLayer

    source = zeit.content.portraitbox.interfaces.portraitboxSource
    expected_types = ['portraitbox']


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=PortraitboxLayer))
    suite.addTest(unittest.makeSuite(PortraitboxSourceTest))
    return suite
