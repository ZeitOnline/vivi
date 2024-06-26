from unittest import mock

import zope.security
import zope.security.proxy

from zeit.content.portraitbox.interfaces import IPortraitboxReference
from zeit.content.portraitbox.portraitbox import Portraitbox
from zeit.content.portraitbox.reference import PortraitboxReference
import zeit.cms.testcontenttype.testcontenttype
import zeit.content.portraitbox.testing


class ReferenceTest(zeit.content.portraitbox.testing.FunctionalTestCase):
    def test_should_have_security_declarations(self):
        ref = PortraitboxReference(mock.Mock())
        ref_proxied = zope.security.proxy.ProxyFactory(ref)
        # If a security declaration exists, read or write access can be
        # decided even though we don't care about the precise outcome of that
        # (which is a matter of test user, security policy etc). Without a
        # security declaration, ForbiddenAttribute would be raised.
        self.assertNothingRaised(zope.security.canAccess, ref_proxied, 'portraitbox')
        self.assertNothingRaised(zope.security.canWrite, ref_proxied, 'portraitbox')

    def test_content_has_portraitbox(self):
        pb = Portraitbox()
        pb.name = 'Everyone'
        pb.text = '<p><strong>Everyone</strong> wants cookies.</p>'
        pb.image = self.repository['2006']['DSC00109_2.JPG']
        self.repository['pb'] = pb
        content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
        pb_ref = IPortraitboxReference(content)
        pb_ref.portraitbox = pb
        self.assertEqual(pb, pb_ref.portraitbox)
        self.repository['foo'] = content
        self.assertEqual(pb, IPortraitboxReference(self.repository['foo']).portraitbox)
