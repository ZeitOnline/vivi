from unittest import mock
from zeit.cms.testing import copy_inherited_functions
import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.infobox.interfaces


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(bases=(zeit.cms.testing.CONFIG_LAYER,))
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(bases=(ZCML_LAYER,))
WSGI_LAYER = zeit.cms.testing.WSGILayer(bases=(ZOPE_LAYER,))


class InfoboxSourceTest(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER

    source = zeit.content.infobox.interfaces.infoboxSource
    expected_types = ['infobox']

    copy_inherited_functions(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase, locals())


class ReferenceTest(zeit.cms.testing.FunctionalTestCase):

    layer = ZOPE_LAYER

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
        layer=ZOPE_LAYER))
    suite.addTest(unittest.makeSuite(InfoboxSourceTest))
    suite.addTest(unittest.makeSuite(ReferenceTest))
    return suite
