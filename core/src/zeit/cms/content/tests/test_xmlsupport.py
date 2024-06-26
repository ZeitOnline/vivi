from unittest import mock
import unittest

import persistent
import zope.security.proxy

import zeit.cms.content.xmlsupport


class PersistentTest(unittest.TestCase):
    def setUp(self):
        self.p = zeit.cms.content.xmlsupport.Persistent()

    def test_propagation(self):
        self.p.__parent__ = persistent.Persistent()
        self.assertEqual(self.p._p_changed, False)  # Unsaved --> False
        self.p._p_changed = True
        # Since the underlying object is unsaved we cannot set to True
        self.assertEqual(self.p._p_changed, False)
        # Assign a jar, so we can save
        self.p.__parent__._p_jar = mock.Mock()
        self.p._p_changed = True
        self.assertEqual(self.p._p_changed, True)
        self.assertEqual(self.p.__parent__._p_changed, True)

    def test_proxied(self):
        parent = persistent.Persistent()
        parent._p_jar = mock.Mock()
        self.p.__parent__ = zope.security.proxy.ProxyFactory(parent)
        self.p._p_changed = True
        self.assertEqual(self.p._p_changed, True)
        self.assertEqual(parent._p_changed, True)
        self.assertEqual(self.p._p_jar, parent._p_jar)

    def test_no_parent(self):
        self.p._p_changed = True
        self.assertTrue(self.p._p_changed is None)
        self.assertTrue(self.p._p_jar is None)

    def test_setattr_marks_change(self):
        self.p.__parent__ = persistent.Persistent()
        self.p.__parent__._p_jar = mock.Mock()
        self.p.foo = 'bar'
        self.assertEqual(self.p._p_changed, True)
        self.assertEqual(self.p.__parent__._p_changed, True)
        self.assertEqual(self.p._p_jar, self.p.__parent__._p_jar)

    def test_p_jar_not_settable(self):
        def set_jar():
            self.p._p_jar = mock.Mock()

        self.assertRaises(AttributeError, set_jar)
