import zeit.cms.checkout.xmlrpc.testing


class XMLRPCTest(zeit.cms.checkout.xmlrpc.testing.BrowserTestCase):
    def test_notify_cms_about_content_modified(self):
        unique_id = 'http://xml.zeit.de/testcontent'
        self.content_modified_request(unique_id)
        self.assertTrue(self.resource_invalidate.called)
        self.assertEqual(unique_id, self.resource_invalidate.call_args.args[0].id)
        self.assertTrue(self.content_modified.called)
        self.assertEqual(unique_id, self.content_modified.call_args.args[0].object.uniqueId)
        self.assertTrue(self.update_index.called)
        self.assertEqual(unique_id, self.update_index.call_args.args[0].object.uniqueId)
