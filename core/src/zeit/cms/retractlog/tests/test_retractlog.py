from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import IPublishInfo
import zeit.cms.retractlog.retractlog
import zeit.cms.testing


class RetractLogTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_start_job_retracts_urls(self):
        self.repository['foo'] = ExampleContentType()
        self.repository['bar'] = ExampleContentType()
        IPublishInfo(self.repository['bar']).published = True
        IPublishInfo(self.repository['foo']).published = True
        job = zeit.cms.retractlog.retractlog.Job()
        job.urls = ['http://xml.zeit.de/foo', 'http://xml.zeit.de/bar']
        job.start()
        self.assertFalse(IPublishInfo(self.repository['foo']).published)
        self.assertFalse(IPublishInfo(self.repository['bar']).published)
