# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
from zope.testing import doctest
import mock
import persistent
import re
import unittest
import zeit.cms.checkout.helper
import zeit.cms.content.xmlsupport
import zeit.cms.repository.interfaces
import zeit.cms.repository.unknown
import zeit.cms.testing
import zope.app.testing.functional
import zope.component
import zope.interface
import zope.security.management
import zope.security.proxy
import zope.testing.renormalizing


checker = zope.testing.renormalizing.RENormalizing([
    (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
     "<GUID>"),])


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



class PersistentTest(unittest.TestCase):

    def setUp(self):
        self.p = zeit.cms.content.xmlsupport.Persistent()

    def test_propagation(self):
        self.p.__parent__ = persistent.Persistent()
        self.assertEquals(self.p._p_changed, False)  # Unsaved --> False
        self.p._p_changed = True
        # Since the underlying object is unsaved we cannot set to True
        self.assertEquals(self.p._p_changed, False)
        # Assign a jar, so we can save
        self.p.__parent__._p_jar = mock.Mock()
        self.p._p_changed = True
        self.assertEquals(self.p._p_changed, True)
        self.assertEquals(self.p.__parent__._p_changed, True)

    def test_proxied(self):
        parent =  persistent.Persistent()
        parent._p_jar = mock.Mock()
        self.p.__parent__ = zope.security.proxy.ProxyFactory(parent)
        self.p._p_changed = True
        self.assertEquals(self.p._p_changed, True)
        self.assertEquals(parent._p_changed, True)
        self.assertEquals(self.p._p_jar, parent._p_jar)

    def test_no_parent(self):
        self.p._p_changed = True
        self.assertTrue(self.p._p_changed is None)
        self.assertTrue(self.p._p_jar is None)

    def test_setattr_marks_change(self):
        self.p.__parent__ = persistent.Persistent()
        self.p.__parent__._p_jar = mock.Mock()
        self.p.foo = 'bar'
        self.assertEquals(self.p._p_changed, True)
        self.assertEquals(self.p.__parent__._p_changed, True)
        self.assertEquals(self.p._p_jar, self.p.__parent__._p_jar)

    def test_p_jar_not_settable(self):
        def set_jar():
            self.p._p_jar = mock.Mock()
        self.assertRaises(AttributeError, set_jar)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'adapter.txt',
        'keyword.txt',
        'lxmlpickle.txt',
        'property.txt',
        optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
                     doctest.ELLIPSIS),
        setUp=zeit.cms.testing.setUp))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'dav.txt',
        'field.txt',
        'liveproperty.txt',
        'metadata.txt',
        'semanticchange.txt',
        'sources.txt',
        'xmlsupport.txt',
        'contentuuid.txt',
        checker=checker,
    ))
    suite.addTest(unittest.makeSuite(DAVTest))
    suite.addTest(unittest.makeSuite(PersistentTest))
    return suite
