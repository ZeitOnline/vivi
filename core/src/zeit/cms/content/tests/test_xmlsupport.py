# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import mock
import persistent
import unittest
import zeit.cms.content.xmlsupport
import zope.security.proxy


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
        parent = persistent.Persistent()
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


class LivePropertyXMLSync(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(LivePropertyXMLSync, self).setUp()
        manager = zope.component.getUtility(
            zeit.cms.content.interfaces.ILivePropertyManager)
        manager.register_live_property('foo', 'bar', WRITEABLE_ALWAYS)

    def test_always_writeable_writes_workingcopy_value_to_xml(self):
        content = self.repository['testcontent']
        properties = zeit.connector.interfaces.IWebDAVProperties(content)
        properties[('foo', 'bar')] = 'one'
        with zeit.cms.checkout.helper.checked_out(content) as co:
            wc_properties = zeit.connector.interfaces.IWebDAVProperties(co)
            wc_properties[('foo', 'bar')] = 'two'
        content = self.repository['testcontent']
        attr = content.xml.xpath('//head/attribute[@name="foo"]')[0]
        self.assertEqual('two', attr.text)
