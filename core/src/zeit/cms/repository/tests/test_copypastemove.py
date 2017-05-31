from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import mock
import zeit.cms.testing
import zope.copypastemove.interfaces


class TestDeleteObjectlog(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super(TestDeleteObjectlog, self).setUp()
        self.patch = mock.patch('zeit.objectlog.objectlog.ObjectLog.delete')
        self.delete = self.patch.start()

    def tearDown(self):
        self.patch.stop()
        super(TestDeleteObjectlog, self).tearDown()

    def test_deletes_on_delete(self):
        del self.repository['testcontent']
        self.assertTrue(self.delete.called)
