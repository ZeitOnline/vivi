# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.checkout.helper
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.unknown
import zeit.cms.testing
import zeit.cms.type
import zeit.connector.interfaces
import zope.component
import zope.interface


class ITestInterface(zope.interface.Interface):
    pass


class StoreProvidedInterfacesTest(zeit.cms.testing.ZeitCmsFunctionalTestCase):

    def setUp(self):
        super(StoreProvidedInterfacesTest, self).setUp()
        self.content = zeit.cms.repository.unknown.PersistentUnknownResource(
            u'data')
        # avoid messing with interfaces (self.repository provides IZONSection,
        # so it would apply section marker interfaces to all content)
        self.section_patcher = mock.patch(
            'zeit.cms.section.section.apply_markers')
        self.section_patcher.start()

    def tearDown(self):
        self.section_patcher.stop()
        super(StoreProvidedInterfacesTest, self).tearDown()

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
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        resource = connector[f_remote.uniqueId]
        event = zeit.cms.repository.interfaces.AfterObjectConstructedEvent(
            f_remote, resource)
        zeit.cms.type.restore_provided_interfaces_from_dav(f_remote, event)
        self.assertEquals(f_remote.__class__, f_remote.__provides__._cls)

    def test_checkout_checkin_keeps_provides(self):
        zope.interface.alsoProvides(self.content, ITestInterface)
        self.repository['foo'] = self.content
        content = self.repository['foo']
        self.assertTrue(ITestInterface.providedBy(self.repository['foo']))
        with zeit.cms.checkout.helper.checked_out(content) as co:
            self.assertTrue(ITestInterface.providedBy(co))
        self.assertTrue(ITestInterface.providedBy(self.repository['foo']))
