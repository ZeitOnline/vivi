import zeit.cms.testing


class WorkflowCopyBrowserTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_reset_publishinfo_works_with_security(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/online/@@copy?unique_id='
            'http://xml.zeit.de/testcontent'
        )
        self.assertEqual('http://localhost/++skin++vivi/repository/online/testcontent', b.url)
