# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
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


class ReferenceTest(zeit.cms.testing.FunctionalTestCase):

    layer = InfoboxLayer

    def test_should_have_security_desclarations(self):
        from zeit.content.infobox.reference import InfoboxReference
        import zope.security
        import zope.security.proxy
        ref = InfoboxReference(mock.Mock)
        ref_proxied = zope.security.proxy.ProxyFactory(ref)
        # A False value indicates that currently there is no access but that
        # there is a way to get access with the right permission. Otherwise
        # ForbiddenAttribute is raised.
        self.assertFalse(zope.security.canAccess(ref_proxied, 'infobox'))
        self.assertFalse(zope.security.canWrite(ref_proxied, 'infobox'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=InfoboxLayer))
    suite.addTest(unittest.makeSuite(InfoboxSourceTest))
    suite.addTest(unittest.makeSuite(ReferenceTest))
    return suite
