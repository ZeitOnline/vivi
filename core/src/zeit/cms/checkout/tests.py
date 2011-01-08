# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.app.locking.interfaces
import zope.app.testing.functional
import zope.component
import zope.security.management
import zope.security.testing


class TestHelper(zope.app.testing.functional.BrowserTestCase):

    layer = zeit.cms.testing.cms_layer

    def setUp(self):
        super(TestHelper, self).setUp()
        self.setSite(self.getRootFolder())
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        principal = zeit.cms.testing.create_interaction(u'zope.user')

    def tearDown(self):
        zeit.cms.testing.tearDown(self)
        self.setSite(None)
        super(TestHelper, self).tearDown()

    def test_changes(self):
        content = self.repository['testcontent']
        self.assertEqual(self.repository, content.__parent__)
        self.assertTrue(self.repository['testcontent'].title is None)
        with zeit.cms.checkout.helper.checked_out(content) as co:
            self.assertNotEqual(self.repository, co.__parent__)
            co.title = u'foo'
        self.assertEqual(u'foo', self.repository['testcontent'].title)
        sc = zeit.cms.content.interfaces.ISemanticChange(content)
        self.assertTrue(sc.last_semantic_change is None)

    def test_checkout_without_change(self):
        content = self.repository['testcontent']
        self.assertEqual(None, self.repository['testcontent'].title)
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.title = u'foo'
            raise zeit.cms.checkout.interfaces.NotChanged
        self.assertTrue(self.repository['testcontent'].title is None)

    def test_checkout_helper_on_locked_doesnt_do_anyting(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.lock('http://xml.zeit.de/testcontent', 'frodo', None)
        with zeit.cms.checkout.helper.checked_out(
            self.repository['testcontent']) as co:
            self.assertTrue(co is None)

    def test_semantic_change(self):
        content = self.repository['testcontent']
        sc = zeit.cms.content.interfaces.ISemanticChange(content)
        self.assertTrue(sc.last_semantic_change is None)
        with zeit.cms.checkout.helper.checked_out(content,
                                                  semantic_change=True) as co:
            pass
        self.assertFalse(sc.last_semantic_change is None)

    def test_old_style_without_change(self):
        content = self.repository['testcontent']
        self.assertEqual(None, self.repository['testcontent'].title)
        def set_title_and_return_false(co):
            co.title = u'foo'
            return False
        zeit.cms.checkout.helper.with_checked_out(
            content, set_title_and_return_false)
        self.assertTrue(self.repository['testcontent'].title is None)

    def test_ignore_conflict(self):
        content = self.repository['testcontent']
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        # Assign an etag
        with zeit.cms.checkout.helper.checked_out(content):
            pass
        def cycle_without_ignore_raises():
            with zeit.cms.checkout.helper.checked_out(content) as co:
                # Change the etag to provoke a conflict
                zeit.connector.interfaces.IWebDAVProperties(co)[
                    ('getetag', 'DAV:')] = 'foo'
        self.assertRaises(
            zeit.cms.repository.interfaces.ConflictError,
            cycle_without_ignore_raises)
        with zeit.cms.checkout.helper.checked_out(content,
                                                  ignore_conflicts=True) as co:
            # Change the etag to provoke a conflict. No exception will be
            # raised due to ignore_conflicts=True
            zeit.connector.interfaces.IWebDAVProperties(co)[
                ('getetag', 'DAV:')] = 'foo'



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'manager.txt'))
    suite.addTest(unittest.makeSuite(TestHelper))
    return suite
