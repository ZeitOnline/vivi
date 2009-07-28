# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.infobox.interfaces
import zope.app.testing.functional


InfoboxLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'InfoboxLayer', allow_teardown=True)


class InfoboxSourceTest(
    zeit.cms.content.tests.test_contentsource.ContentSourceTest):

    layer = InfoboxLayer

    source = zeit.content.infobox.interfaces.infoboxSource
    expected_types = ['infobox']


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=InfoboxLayer))
    suite.addTest(unittest.makeSuite(InfoboxSourceTest))
    return suite
