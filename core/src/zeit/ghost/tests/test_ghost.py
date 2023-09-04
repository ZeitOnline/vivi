from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.checkout.interfaces
import zeit.ghost.ghost
import zeit.ghost.testing


class GhostbusterTest(zeit.ghost.testing.FunctionalTestCase):

    def test_removes_excessive_ghosts_on_checkout(self):
        self.repository['ghost-origin'] = ExampleContentType()
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        for _ in range(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE * 2):
            with mock.patch('zeit.ghost.ghost._remove_excessive_ghosts'):
                zeit.ghost.ghost.create_ghost(self.repository['ghost-origin'])
        self.assertEqual(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE * 2, len(wc))
        with checked_out(
                self.repository['testcontent'], events=True, temporary=False):
            self.assertEqual(
                zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE, len(wc))

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
