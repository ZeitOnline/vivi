# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import grokcore.component.testing
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.connector.interfaces
import zope.component
import zope.interface
import zope.security.proxy


class ITestInterface(zope.interface.Interface):
    pass


class TestPropertyBase(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super(TestPropertyBase, self).setUp()
        self.content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')

    def test_adapter_grokking(self):
        class Adapter(zeit.cms.content.dav.DAVPropertiesAdapter):
            grokcore.component.implements(ITestInterface)

        self.assertRaises(TypeError, ITestInterface, self.content)
        grokcore.component.testing.grok_component('adapter', Adapter)
        adapter = ITestInterface(self.content)
        self.assertTrue(isinstance(adapter, Adapter))
        # When content is proxied, the adapter will be proxied (trusted
        # adapter)
        adapter = ITestInterface(zope.security.proxy.ProxyFactory(
            self.content))
        self.assertFalse(isinstance(adapter, Adapter))
        self.assertTrue(isinstance(zope.security.proxy.removeSecurityProxy(
            adapter), Adapter))
        self.assertEquals(self.content, adapter.__parent__)
        # Unregister adapter so we don't leak it
        self.assertTrue(
            zope.component.getSiteManager().unregisterAdapter(
                Adapter, (zeit.cms.repository.interfaces.IDAVContent,),
                ITestInterface))
        self.assertRaises(TypeError, ITestInterface, self.content)

    def test_adapter_grokking_isolation(self):
        # Make sure the previous test does not leak the adapter registration
        self.assertRaises(TypeError, ITestInterface, self.content)

    def test_adapter_adaptable_to_properties(self):
        adapter = zeit.cms.content.dav.DAVPropertiesAdapter(self.content)
        zeit.connector.interfaces.IWebDAVProperties(adapter)

    def test_adapter_should_set_parent(self):
        adapter = zeit.cms.content.dav.DAVPropertiesAdapter(self.content)
        self.assertEqual(self.content, adapter.__parent__)
