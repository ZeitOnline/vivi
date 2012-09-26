# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.checkout.interfaces import CheckinCheckoutError
from zeit.cms.checkout.interfaces import ICheckinManager, ICheckoutManager
from zeit.cms.checkout.interfaces import IValidateCheckinEvent
import copy
import datetime
import zeit.cms.checkout.helper
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.cms.workingcopy.interfaces
import zope.component


class IContent(zeit.cms.interfaces.ICMSContent):
    pass


class Content(object):

    zope.interface.implements(
        IContent, zope.annotation.interfaces.IAttributeAnnotatable)
    uniqueId = u'testcontent://'
    __name__ = u'karlheinz'


@zope.component.adapter(IContent)
@zope.interface.implementer(zeit.cms.checkout.interfaces.ILocalContent)
def local_content(context):
    local = copy.copy(context)
    local.are_you_local = True
    zope.interface.alsoProvides(
        local, zeit.cms.checkout.interfaces.ILocalContent)
    return local


@zope.component.adapter(IContent)
@zope.interface.implementer(zeit.cms.checkout.interfaces.IRepositoryContent)
def repository_content(context):
    content = copy.copy(context)
    content.are_you_local = False
    zope.interface.noLongerProvides(
        content, zeit.cms.checkout.interfaces.ILocalContent)
    return content


class ManagerTest(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(ManagerTest, self).setUp()
        self.content = Content()
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(local_content)
        gsm.registerAdapter(repository_content)

    def tearDown(self):
        self._tear_down_adapters()
        super(ManagerTest, self).tearDown()

    def _tear_down_adapters(self):
        gsm = zope.component.getGlobalSiteManager()
        gsm.unregisterAdapter(local_content)
        gsm.unregisterAdapter(repository_content)

    def test_checkout_without_ILocalContent_adapter_should_raise(self):
        self._tear_down_adapters()
        manager = ICheckoutManager(self.content)
        self.assertFalse(manager.canCheckout)
        self.assertRaises(CheckinCheckoutError, manager.checkout)

    def test_checkout_needs_adapter_to_ILocalContent(self):
        manager = ICheckoutManager(self.content)
        checked_out = manager.checkout()
        self.assertTrue(checked_out.are_you_local)

    def test_checkin_without_IRepositoryContent_adapter_should_raise(self):
        manager = ICheckoutManager(self.content)
        checked_out = manager.checkout()
        self._tear_down_adapters()
        manager = ICheckinManager(checked_out)
        self.assertTrue(manager.canCheckin)
        self.assertRaises(LookupError, manager.checkin)

    def test_checkin_needs_adapter_to_IRepositoryContent(self):
        manager = ICheckoutManager(self.content)
        checked_out = manager.checkout()
        manager = ICheckinManager(checked_out)
        checked_in = manager.checkin()
        self.assertFalse(checked_in.are_you_local)


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


class SemanticChangeTest(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(SemanticChangeTest, self).setUp()
        self.content = self.repository['testcontent']
        self.sc = zeit.cms.content.interfaces.ISemanticChange(self.content)

    def test_content_has_no_semantic_change_by_default(self):
        self.assertIsNone(self.sc.last_semantic_change)

    def test_checkin_with_semantic_change_sets_lsc_date(self):
        with zeit.cms.checkout.helper.checked_out(
            self.content, semantic_change=True):
            pass
        self.assertIsInstance(self.sc.last_semantic_change, datetime.datetime)

    def test_checkin_without_semantic_change_does_not_change_lsc_date(self):
        old = self.sc.last_semantic_change
        with zeit.cms.checkout.helper.checked_out(
            self.content, semantic_change=False):
            pass
        self.assertEqual(old, self.sc.last_semantic_change)

    def test_checkin_without_explicit_sc_uses_sc_flag_on_content_object(self):
        with zeit.cms.checkout.helper.checked_out(
            self.content, semantic_change=None) as co:
            sc = zeit.cms.content.interfaces.ISemanticChange(co)
            sc.has_semantic_change = True
        self.assertIsInstance(self.sc.last_semantic_change, datetime.datetime)
