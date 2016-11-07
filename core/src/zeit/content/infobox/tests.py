from zeit.cms.testing import copy_inherited_functions
import mock
import unittest
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.infobox.interfaces


InfoboxLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=zeit.cms.testing.cms_product_config)


class InfoboxSourceTest(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        zeit.cms.testing.FunctionalTestCase):

    layer = InfoboxLayer

    source = zeit.content.infobox.interfaces.infoboxSource
    expected_types = ['infobox']

    copy_inherited_functions(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase, locals())


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
