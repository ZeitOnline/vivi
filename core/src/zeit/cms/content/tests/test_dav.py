# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import grokcore.component
import grokcore.component.testing
import zeit.cms.checkout.helper
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.unknown
import zeit.cms.testing
import zeit.connector.interfaces
import zope.component
import zope.interface
import zope.security.proxy


class ITestInterface(zope.interface.Interface):
    pass


class DAVTest(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(DAVTest, self).setUp()
        self.content = zeit.cms.repository.unknown.PersistentUnknownResource(
            u'data')

    def tearDown(self):
        super(DAVTest, self).tearDown()

    def test_provides_stored_in_property(self):
        zope.interface.alsoProvides(self.content, ITestInterface)
        self.repository['foo'] = self.content
        content = self.repository['foo']
        properties = zeit.connector.interfaces.IWebDAVProperties(content)
        self.assertTrue(('provides', 'http://namespaces.zeit.de/CMS/meta')
                        in properties)
        self.assertTrue(
            properties[('provides',
                        'http://namespaces.zeit.de/CMS/meta')].startswith(
                            '<pickle>'))
        self.assertTrue(ITestInterface.providedBy(content))
        # Getting the content again doesn't change the proviedes:
        self.assertTrue(ITestInterface.providedBy(self.repository['foo']))

    def test_unchanged_provides_does_not_overwrite_implements(self):
        self.repository['foo'] = self.content
        self.assertTrue(
            zeit.cms.interfaces.ICMSContent.providedBy(self.repository['foo']))

    def test_unchanged_provides_does_not_store_property(self):
        self.repository['foo'] = self.content
        properties = zeit.connector.interfaces.IWebDAVProperties(self.content)
        self.assertEquals(
            zeit.connector.interfaces.DeleteProperty,
            properties[('provides', 'http://namespaces.zeit.de/CMS/meta')])

    def test_changed_and_reset_provides_does_not_overwrite_implements(self):
        zope.interface.alsoProvides(self.content, ITestInterface)
        zope.interface.noLongerProvides(self.content, ITestInterface)
        self.repository['foo'] = self.content
        self.assertTrue(
            zeit.cms.interfaces.ICMSContent.providedBy(self.repository['foo']))

    def test_store_object_from_repository(self):
        self.repository['foo'] = self.content
        content = self.repository['foo']
        zope.interface.alsoProvides(content, ITestInterface)
        self.repository['foo'] = content

    def test_local_content(self):
        zope.interface.alsoProvides(
            self.content, zeit.cms.workingcopy.interfaces.ILocalContent)
        self.repository['foo'] = self.content
        self.assertFalse(
            zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(
                self.repository['foo']))
        # The object which was added itself keeps its ILocalContent
        self.assertTrue(
            zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(
                self.content))

    def test_file(self):
        f = zeit.cms.repository.file.LocalFile()
        f.open('w').write('data')
        zope.interface.alsoProvides(f, ITestInterface)
        self.repository['foo'] = f
        f = self.repository['foo']
        self.assertEqual(True, ITestInterface.providedBy(f))
        self.assertEqual(
            False, zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(f))

        f = zeit.cms.repository.file.LocalFile(f.uniqueId)
        zope.interface.alsoProvides(f, ITestInterface)
        self.repository['foo'] = f
        f = self.repository['foo']
        self.assertEqual(True, ITestInterface.providedBy(f))
        self.assertEqual(
            False, zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(f))

    def test_restore_returns_provides_with_correct_class(self):
        f_local = zeit.cms.repository.file.LocalFile()
        f_local.open('w').write('blub')
        zope.interface.alsoProvides(f_local, ITestInterface)
        self.repository['file'] = f_local
        f_remote = self.repository['file']
        resource = self.connector[f_remote.uniqueId]
        event = zeit.cms.repository.interfaces.AfterObjectConstructedEvent(
            f_remote, resource)
        zeit.cms.content.dav.restore_provides_from_dav(f_remote, event)
        self.assertEquals(f_remote.__class__, f_remote.__provides__._cls)

    def test_checkout_checkin_keeps_provides(self):
        zope.interface.alsoProvides(self.content, ITestInterface)
        self.repository['foo'] = self.content
        content = self.repository['foo']
        self.assertTrue(ITestInterface.providedBy(self.repository['foo']))
        with zeit.cms.checkout.helper.checked_out(content) as co:
            self.assertTrue(ITestInterface.providedBy(co))
        self.assertTrue(ITestInterface.providedBy(self.repository['foo']))

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @property
    def connector(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IConnector)


class TestPropertyBase(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(TestPropertyBase, self).setUp()
        self.content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')

    def test_adapter_grokking(self):

        import zeit.cms.content.dav
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
            zope.component.getGlobalSiteManager().unregisterAdapter(
                Adapter, (zeit.cms.repository.interfaces.IDAVContent,),
                ITestInterface))
        self.assertRaises(TypeError, ITestInterface, self.content)

    def test_adapter_grokking_isolation(self):
        # Make sure the previous test does not leak the adapter registration
        self.assertRaises(TypeError, ITestInterface, self.content)

    def test_adatper_adaptable_to_properties(self):
        adapter = zeit.cms.content.dav.DAVPropertiesAdapter(self.content)
        properties = zeit.connector.interfaces.IWebDAVProperties(adapter)

    def test_adatper_should_set_parent(self):
        adapter = zeit.cms.content.dav.DAVPropertiesAdapter(self.content)
        self.assertEqual(self.content, adapter.__parent__)
