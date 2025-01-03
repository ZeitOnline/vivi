from pendulum import datetime
import transaction
import zope.event

from zeit.cms.checkout.helper import checked_out
import zeit.cms.testing
import zeit.cms.workflow.interfaces


class LastSemanticPublish(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        zeit.cms.workflow.mock._publish_times['http://xml.zeit.de/testcontent'] = datetime(
            2015, 5, 17
        )

    def test_lsp_is_updated_when_lsc_is_newer(self):
        content = self.repository['testcontent']
        published = zeit.cms.workflow.interfaces.IPublishInfo(content)
        OLD_TIMESTAMP = datetime(2010, 1, 1)
        zeit.cms.workflow.mock._publish_times_semantic[content.uniqueId] = OLD_TIMESTAMP

        with checked_out(content, semantic_change=True, temporary=False):
            # force update of semantic_change to now():
            # commit updates IDCTimes.modified, which is then written to lsc
            transaction.commit()

        zope.event.notify(zeit.cms.workflow.interfaces.BeforePublishEvent(content, None))
        published = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertGreater(published.date_last_published_semantic, OLD_TIMESTAMP)

    def test_does_not_break_if_lsp_is_none(self):
        content = self.repository['testcontent']
        with checked_out(content, semantic_change=True, temporary=False):
            transaction.commit()
        zope.event.notify(zeit.cms.workflow.interfaces.BeforePublishEvent(content, None))
        published = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertNotEqual(None, published.date_last_published_semantic)


class ModifiedTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_date_last_modified_is_not_updated_during_publish_cycle(self):
        content = self.repository['testcontent']
        mod = zeit.cms.workflow.interfaces.IModified(content)
        self.assertEqual(None, mod.date_last_modified)
        co = zeit.cms.checkout.interfaces.ICheckoutManager(content).checkout()
        zeit.cms.checkout.interfaces.ICheckinManager(co).checkin(publishing=True)
        self.assertEqual(None, mod.date_last_modified)
