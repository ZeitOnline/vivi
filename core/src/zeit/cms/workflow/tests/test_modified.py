from datetime import datetime
from zeit.cms.checkout.helper import checked_out
import pytz
import transaction
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zope.event


class LastSemanticPublish(zeit.cms.testing.ZeitCmsTestCase):

    def test_lsp_is_updated_when_lsc_is_newer(self):
        content = self.repository['testcontent']
        published = zeit.cms.workflow.interfaces.IPublishInfo(content)
        OLD_TIMESTAMP = datetime(2010, 1, 1, tzinfo=pytz.UTC)
        zeit.cms.workflow.mock._publish_times_semantic[content.uniqueId] = \
            OLD_TIMESTAMP

        with checked_out(content, semantic_change=True, temporary=False):
            # force update of semantic_change to now():
            # commit updates IDCTimes.modified, which is then written to lsc
            transaction.commit()

        zope.event.notify(
            zeit.cms.workflow.interfaces.PublishedEvent(content, None))
        published = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertGreater(
            published.date_last_published_semantic, OLD_TIMESTAMP)

    def test_does_not_break_if_lsp_is_none(self):
        content = self.repository['testcontent']
        with checked_out(content, semantic_change=True, temporary=False):
            transaction.commit()
        zope.event.notify(
            zeit.cms.workflow.interfaces.PublishedEvent(content, None))
        published = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertNotEqual(None, published.date_last_published_semantic)
