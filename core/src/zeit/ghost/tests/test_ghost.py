from unittest import mock

import transaction

from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.checkout.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.ghost.ghost
import zeit.ghost.testing


class GhostTest(zeit.ghost.testing.FunctionalTestCase):
    def test_creates_ghost_on_checkin(self):
        workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)
        with checked_out(self.repository['testcontent'], temporary=False):
            self.assertEqual(['testcontent'], list(workingcopy))
        transaction.commit()

        self.assertEqual(['testcontent'], list(workingcopy))
        ghost = workingcopy['testcontent']
        self.assertTrue(zeit.ghost.interfaces.IGhost.providedBy(ghost))
        self.assertTrue(zeit.cms.clipboard.interfaces.IClipboardEntry.providedBy(ghost))

        with checked_out(self.repository['testcontent'], temporary=False):
            self.assertEqual(['testcontent'], list(workingcopy))
            self.assertFalse(zeit.ghost.interfaces.IGhost.providedBy(workingcopy['testcontent']))

    def test_temporary_checkout_does_not_create_ghost(self):
        workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)
        with checked_out(self.repository['testcontent'], temporary=True):
            pass
        transaction.commit()
        self.assertEqual([], list(workingcopy))


class GhostbusterTest(zeit.ghost.testing.FunctionalTestCase):
    def test_removes_excessive_ghosts_on_checkout(self):
        self.repository['ghost-origin'] = ExampleContentType()
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        for _ in range(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE * 2):
            with mock.patch('zeit.ghost.ghost._remove_excessive_ghosts'):
                zeit.ghost.ghost.create_ghost(self.repository['ghost-origin'])
        self.assertEqual(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE * 2, len(wc))
        with checked_out(self.repository['testcontent'], events=True, temporary=False):
            self.assertEqual(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE, len(wc))

    def test_removes_excessive_ghosts_when_creating_ghosts(self):
        # This is important for ImageGroups, see VIV-489.
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        for _ in range(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE * 2):
            zeit.ghost.ghost.create_ghost(self.repository['testcontent'])
        self.assertEqual(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE + 1, len(wc))

    def test_removes_excessive_ghosts_before_creating_ghosts(self):
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        for i in range(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE):
            name = 'test-%s' % i
            self.repository[name] = ExampleContentType()
            ICheckoutManager(self.repository[name]).checkout()

        zeit.ghost.ghost.create_ghost(self.repository['testcontent'])
        self.assertEqual(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE + 1, len(wc))

    def test_removes_broken_ghost_on_checkout(self):
        workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)
        self.repository['c1'] = ExampleContentType()
        self.repository['c2'] = ExampleContentType()

        for name in ['c1', 'c2']:
            with checked_out(self.repository[name], temporary=False):
                pass
        transaction.commit()

        self.assertEqual(['c1', 'c2'], sorted(list(workingcopy)))
        del self.repository['c2']
        transaction.commit()
        self.assertEqual(['c1', 'c2'], sorted(list(workingcopy)))

        with checked_out(self.repository['c1'], temporary=False):
            self.assertEqual(['c1'], list(workingcopy))
