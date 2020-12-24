from unittest import mock
from zeit.cms.testing import copy_inherited_functions
import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.image.testing
import zeit.content.portraitbox.interfaces


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(
    zeit.content.image.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class PortraitboxSourceTest(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER

    source = zeit.content.portraitbox.interfaces.portraitboxSource
    expected_types = ['portraitbox']

    copy_inherited_functions(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase, locals())


class ReferenceTest(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER

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
        layer=ZOPE_LAYER))
    suite.addTest(unittest.makeSuite(PortraitboxSourceTest))
    suite.addTest(unittest.makeSuite(ReferenceTest))
    return suite
