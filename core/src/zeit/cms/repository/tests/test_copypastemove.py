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

    def test_deletes_on_move(self):
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(
            self.repository)
        renamer.renameItem('testcontent', 'moved')
        self.assertTrue(self.delete.called)
        self.assertEqual(
            'http://xml.zeit.de/testcontent',
            self.delete.call_args[0][0].referenced_object)

    def test_does_not_delete_on_add(self):
        self.repository['second'] = ExampleContentType()
        self.assertFalse(self.delete.called)
