from unittest import mock

import zope.security
import zope.security.proxy

from zeit.content.infobox.reference import InfoboxReference
import zeit.content.infobox.testing


class ReferenceTest(zeit.content.infobox.testing.FunctionalTestCase):
    def test_should_have_security_declarations(self):
        ref = InfoboxReference(mock.Mock())
        ref_proxied = zope.security.proxy.ProxyFactory(ref)
        # If a security declaration exists, read or write access can be
        # decided even though we don't care about the precise outcome of that
        # (which is a matter of test user, security policy etc). Without a
        # security declaration, ForbiddenAttribute would be raised.
        self.assertNothingRaised(zope.security.canAccess, ref_proxied, 'infobox')
        self.assertNothingRaised(zope.security.canWrite, ref_proxied, 'infobox')
