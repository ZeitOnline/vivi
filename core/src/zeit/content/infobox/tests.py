# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import pkg_resources
import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.infobox.interfaces


InfoboxLayer = zeit.cms.testing.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'InfoboxLayer', allow_teardown=True)


class InfoboxSourceTest(
    zeit.cms.content.tests.test_contentsource.ContentSourceTest):

    layer = InfoboxLayer

    source = zeit.content.infobox.interfaces.infoboxSource
    expected_types = ['infobox']


class ReferenceTest(zeit.cms.testing.FunctionalTestCase):

    layer = InfoboxLayer

    def test_should_have_security_declarations(self):
        from zeit.content.infobox.reference import InfoboxReference
        import zope.security
        import zope.security.proxy
        ref = InfoboxReference(mock.Mock)
        ref_proxied = zope.security.proxy.ProxyFactory(ref)
        # If a security declaration exists, read or write access can be
        # decided even though we don't care about the precise outcome of that
        # (which is a matter of test user, security policy etc). Without a
        # security declaration, ForbiddenAttribute would be raised.
        self.assertNothingRaised(
            zope.security.canAccess, ref_proxied, 'infobox')
        self.assertNothingRaised(
            zope.security.canWrite, ref_proxied, 'infobox')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=InfoboxLayer))
    suite.addTest(unittest.makeSuite(InfoboxSourceTest))
    suite.addTest(unittest.makeSuite(ReferenceTest))
    return suite
