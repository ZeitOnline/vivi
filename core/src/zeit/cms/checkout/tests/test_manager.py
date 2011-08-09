# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.checkout.interfaces import CheckinCheckoutError
from zeit.cms.checkout.interfaces import IValidateCheckinEvent
from zeit.cms.checkout.interfaces import ICheckinManager, ICheckoutManager
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.cms.workingcopy.interfaces
import zope.component


class ValidateCheckinTest(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(ValidateCheckinTest, self).setUp()
        zope.component.getSiteManager().registerHandler(
            self.provoke_veto, (IValidateCheckinEvent,))

        self.workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(
            self.principal)

        manager = ICheckoutManager(self.repository['testcontent'])
        self.checked_out = manager.checkout()

    def tearDown(self):
        zope.component.getSiteManager().unregisterHandler(
            self.provoke_veto, (IValidateCheckinEvent,))
        super(ValidateCheckinTest, self).tearDown()

    def provoke_veto(self, event):
        event.veto('provoked veto')

    def test_veto_in_event_makes_canCheckin_return_false(self):
        manager = ICheckinManager(self.checked_out)
        self.assertFalse(manager.canCheckin)

    def test_veto_message_is_available_on_manager(self):
        manager = ICheckinManager(self.checked_out)
        manager.canCheckin
        self.assertEqual('provoked veto', manager.last_validation_error)

    def test_checkin_with_veto_should_raise(self):
        self.assertEqual(1, len(self.workingcopy))
        lsc = zeit.cms.content.interfaces.ISemanticChange(
            self.repository['testcontent'])
        changed = lsc.last_semantic_change

        manager = ICheckinManager(self.checked_out)
        self.assertRaisesRegexp(
            CheckinCheckoutError, '.*provoked veto.*', manager.checkin)

        self.assertEqual(1, len(self.workingcopy))

        lsc = zeit.cms.content.interfaces.ISemanticChange(
            self.repository['testcontent'])
        self.assertEqual(changed, lsc.last_semantic_change)
