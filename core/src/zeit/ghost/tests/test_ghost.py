from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import zeit.cms.checkout.interfaces
import zeit.cms.testing
import zeit.ghost.ghost
import zeit.ghost.testing


class GhostbusterTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.ghost.testing.ZCML_LAYER

    def test_removes_excessive_ghosts_on_checkout(self):
        self.repository['ghost-origin'] = TestContentType()
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        for i in range(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE * 2):
            zeit.ghost.ghost.create_ghost(self.repository['ghost-origin'])
        self.assertEqual(zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE * 2, len(wc))
        with checked_out(
                self.repository['testcontent'], events=True, temporary=False):
            self.assertEqual(
                zeit.ghost.ghost.TARGET_WORKINGCOPY_SIZE, len(wc))
