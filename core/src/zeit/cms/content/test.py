# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zope.component
import zeit.cms.repository.unknown
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.app.testing.functional
import zope.interface
from zope.testing import doctest


class ITestInterface(zope.interface.Interface):
    pass


class DAVTest(zope.app.testing.functional.BrowserTestCase):

    layer = zeit.cms.testing.cms_layer

    def setUp(self):
        super(DAVTest, self).setUp()
        self.setSite(self.getRootFolder())
        self.content = zeit.cms.repository.unknown.PersistentUnknownResource(
            u'data')

    def tearDown(self):
        self.setSite(None)
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
            {('provides', 'http://namespaces.zeit.de/CMS/meta'):
                zeit.connector.interfaces.DeleteProperty},
            dict(properties))

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
        self.assertEqual(
            False, zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(
                self.repository['foo']))

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

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @property
    def connector(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IConnector)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'adapter.txt',
        'field.txt',
        'keyword.txt',
        'lxmlpickle.txt',
        'property.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS),
        setUp=zeit.cms.testing.setUp))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'dav.txt',
        'liveproperty.txt',
        'metadata.txt',
        'sources.txt',
        'xmlsupport.txt',
    ))
    suite.addTest(unittest.makeSuite(DAVTest))
    return suite
