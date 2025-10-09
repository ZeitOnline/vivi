import lxml.etree
import transaction
import zope.component

import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.testing


class TestHelper(zeit.cms.testing.ZeitCmsTestCase):
    def test_changes(self):
        content = self.repository['testcontent']
        self.assertEqual(self.repository, content.__parent__)
        self.assertEqual('', self.repository['testcontent'].title)
        with zeit.cms.checkout.helper.checked_out(content) as co:
            self.assertNotEqual(self.repository, co.__parent__)
            co.title = 'foo'
        transaction.commit()
        self.assertEqual('foo', self.repository['testcontent'].title)
        sc = zeit.cms.content.interfaces.ISemanticChange(content)
        self.assertTrue(sc.last_semantic_change is None)

    def test_checkout_without_change(self):
        content = self.repository['testcontent']
        self.assertEqual('', self.repository['testcontent'].title)
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.title = 'foo'
            raise zeit.cms.checkout.interfaces.NotChanged
        self.assertEqual('', self.repository['testcontent'].title)

    def test_checkout_helper_on_locked_doesnt_do_anyting(self):
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        connector.lock('http://xml.zeit.de/testcontent', 'frodo', None)
        with zeit.cms.checkout.helper.checked_out(self.repository['testcontent']) as co:
            self.assertTrue(co is None)

    def test_semantic_change(self):
        content = self.repository['testcontent']
        sc = zeit.cms.content.interfaces.ISemanticChange(content)
        self.assertTrue(sc.last_semantic_change is None)
        with zeit.cms.checkout.helper.checked_out(content, semantic_change=True):
            pass
        self.assertFalse(sc.last_semantic_change is None)

    def test_old_style_without_change(self):
        content = self.repository['testcontent']
        self.assertEqual('', self.repository['testcontent'].title)

        def set_title_and_return_false(co):
            co.title = 'foo'
            return False

        zeit.cms.checkout.helper.with_checked_out(content, set_title_and_return_false)
        self.assertEqual('', self.repository['testcontent'].title)

    def test_ignore_conflict(self):
        c1 = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['testcontent']
        ).checkout()
        c1.xml.replace(c1.xml.find('body'), lxml.etree.fromstring('<body>one</body>'))
        # In reality, the lock would have to time out for this scenario to happen
        self.repository.connector.unlock('http://xml.zeit.de/testcontent')
        transaction.commit()

        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('zope.producer')
        with zeit.cms.checkout.helper.checked_out(self.repository['testcontent']) as c2:
            c2.xml.replace(c2.xml.find('body'), lxml.etree.fromstring('<body>two</body>'))
        transaction.commit()
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('zope.user')

        c1 = zeit.cms.checkout.interfaces.ICheckinManager(c1)
        with self.assertRaises(zeit.cms.repository.interfaces.ConflictError):
            c1.checkin()

        with self.assertNothingRaised():
            c1.checkin(ignore_conflicts=True)
