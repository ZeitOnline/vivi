from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import transaction
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.component


class LeadTimeTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.repository['foo'] = ExampleContentType()
        cp = zeit.content.cp.centerpage.CenterPage()
        zope.interface.alsoProvides(cp, zeit.content.cp.interfaces.ILeadTimeCP)
        factory = zope.component.getAdapter(
            cp['lead'], zeit.edit.interfaces.IElementFactory, name='teaser')
        teaser = factory()
        teaser.insert(0, self.repository['foo'])
        # The validation rules in testing require more than two blocks.
        factory()
        factory()
        self.repository['cp'] = cp

    def publish(self, content):
        IPublishInfo(content).urgent = True
        IPublish(content).publish()
        transaction.commit()

    def test_sets_start_on_lead_article(self):
        self.publish(self.repository['cp'])
        leadtime = zeit.content.cp.interfaces.ILeadTime(self.repository['foo'])
        self.assertNotEqual(None, leadtime.start)
        self.assertEqual(None, leadtime.end)
        self.assertEllipsis(
            '...<attribute...name="leadtime_start">...',
            zeit.cms.testing.xmltotext(self.repository['foo'].xml))

    def test_sets_end_on_article_when_no_longer_in_lead(self):
        self.publish(self.repository['cp'])
        with checked_out(self.repository['cp']) as cp:
            for entry in cp['lead'].values()[0]:
                cp['lead'].values()[0].remove(entry)
        self.publish(self.repository['cp'])
        leadtime = zeit.content.cp.interfaces.ILeadTime(self.repository['foo'])
        self.assertNotEqual(None, leadtime.end)
        self.assertEllipsis(
            '...<attribute...name="leadtime_end">...',
            zeit.cms.testing.xmltotext(self.repository['foo'].xml))

    def test_marks_do_not_change_when_lead_article_not_changed(self):
        self.publish(self.repository['cp'])
        leadtime = zeit.content.cp.interfaces.ILeadTime(self.repository['foo'])
        start = leadtime.start
        self.publish(self.repository['cp'])
        leadtime = zeit.content.cp.interfaces.ILeadTime(self.repository['foo'])
        self.assertEqual(start, leadtime.start)
        self.assertEqual(None, leadtime.end)

    def test_publishes_article_if_already_published(self):
        self.publish(self.repository['foo'])
        before = IPublishInfo(self.repository['foo']).date_last_published
        self.publish(self.repository['cp'])
        after = IPublishInfo(self.repository['foo']).date_last_published
        self.assertGreater(after, before)

    def test_article_checked_out_by_somebody_else_steals_lock_first(self):
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('other')
        ICheckoutManager(self.repository['foo']).checkout()
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('zope.user')
        self.publish(self.repository['cp'])
        self.assertEllipsis(
            '...<attribute...name="leadtime_start">...',
            zeit.cms.testing.xmltotext(self.repository['foo'].xml))

    def test_article_checked_out_already_does_not_update_xml(self):
        ICheckoutManager(self.repository['foo']).checkout()
        self.publish(self.repository['cp'])
        leadtime = zeit.content.cp.interfaces.ILeadTime(self.repository['foo'])
        self.assertNotEqual(None, leadtime.start)
        self.assertNotIn(
            'leadtime_start',
            zeit.cms.testing.xmltotext(self.repository['foo'].xml))
