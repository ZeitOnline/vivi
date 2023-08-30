from unittest import mock
from zeit.content.portraitbox.reference import PortraitboxReference
import zeit.content.portraitbox.testing
import zope.security
import zope.security.proxy


class ReferenceTest(zeit.content.portraitbox.testing.FunctionalTestCase):

    def test_should_have_security_declarations(self):
        ref = PortraitboxReference(mock.Mock())
        ref_proxied = zope.security.proxy.ProxyFactory(ref)
        # If a security declaration exists, read or write access can be
        # decided even though we don't care about the precise outcome of that
        # (which is a matter of test user, security policy etc). Without a
        # security declaration, ForbiddenAttribute would be raised.
        self.assertNothingRaised(
            zope.security.canAccess, ref_proxied, 'portraitbox')
        self.assertNothingRaised(
            zope.security.canWrite, ref_proxied, 'portraitbox')
