import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import ICMSContent
from zeit.revisions.interfaces import IContentRevision
import zeit.cms.checkout.webhook
import zeit.content.cp.centerpage
import zeit.content.link.link
import zeit.revisions
import zeit.revisions.testing


class Revisions(zeit.revisions.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.uuid = zeit.cms.content.interfaces.IUUID(self.article).shortened
        self.revision = zope.component.getUtility(IContentRevision)

    def tearDown(self):
        # clear bucket
        self.revision.bucket.delete_blobs([i for i in self.revision.bucket.list_blobs()])
        return super().tearDown()

    def test_create_revision_after_checkin_for_articles(self):
        with checked_out(self.article) as co:
            co.access = 'abo'  # trigger AfterCheckinEvent
        file_types = ['json', 'xml']
        for file_type in file_types:
            self.assertTrue(self.revision.bucket.blob(f'{self.uuid}.{file_type}').exists())

    def test_create_revision_after_checkin_for_centerpages(self):
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        with checked_out(self.repository['cp']) as co:
            co.access = 'abo'  # trigger AfterCheckinEvent
        file_types = ['json', 'xml']
        uuid = zeit.cms.content.interfaces.IUUID(self.repository['cp']).shortened
        for file_type in file_types:
            self.assertTrue(self.revision.bucket.blob(f'{uuid}.{file_type}').exists())

    def test_create_revision_after_checkin_filter_articles(self):
        filter = zeit.revisions.revisions.FILTERS.factory.getValues()
        filter.add_exclude('type', 'article')
        with checked_out(self.article) as co:
            co.access = 'abo'  # trigger AfterCheckinEvent
        self.assertFalse(self.revision.bucket.blob(f'{self.uuid}.xml').exists())

    def test_create_revision_after_checkin_skip_non_versionable_content(self):
        self.repository['link'] = zeit.content.link.link.Link()
        with checked_out(self.repository['link']) as co:
            co.title = 'foo'  # trigger AfterCheckinEvent
        uuid = zeit.cms.content.interfaces.IUUID(self.repository['link']).shortened
        self.assertFalse(self.revision.bucket.blob(f'{uuid}.xml').exists())

    def test_toggle_safeguard(self):
        FEATURE_TOGGLES.set('disable_revisions_on_checkin')
        with checked_out(self.article) as co:
            co.access = 'abo'  # trigger AfterCheckinEvent
        self.assertFalse(self.revision.bucket.blob(f'{self.uuid}.xml').exists())
