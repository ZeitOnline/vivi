# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
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


class ReferenceTest(zeit.cms.testing.FunctionalTestCase):

    layer = PortraitboxLayer

    def test_should_have_security_declarations(self):
        from zeit.content.portraitbox.reference import PortraitboxReference
        import zope.security
        import zope.security.proxy
        ref = PortraitboxReference(mock.Mock)
        ref_proxied = zope.security.proxy.ProxyFactory(ref)
        # If a security declaration exists, read or write access can be
        # decided even though we don't care about the precise outcome of that
        # (which is a matter of test user, security policy etc). Without a
        # security declaration, ForbiddenAttribute would be raised.
        self.assertNothingRaised(
            zope.security.canAccess, ref_proxied, 'portraitbox')
        self.assertNothingRaised(
            zope.security.canWrite, ref_proxied, 'portraitbox')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=PortraitboxLayer))
    suite.addTest(unittest.makeSuite(PortraitboxSourceTest))
    suite.addTest(unittest.makeSuite(ReferenceTest))
    return suite
