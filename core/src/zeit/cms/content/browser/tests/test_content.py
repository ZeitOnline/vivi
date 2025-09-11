import zeit.cms.testing


class ContentAPI(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_serializes_uuid_to_json(self):
        self.browser.open(
            'http://localhost/@@find_content?url=https://vivi.zeit.de/repository/testcontent/@@view.html'
        )
        self.assert_json(
            {
                'uniqueId': 'http://xml.zeit.de/testcontent',
                'uuid': zeit.cms.content.interfaces.IUUID(self.repository['testcontent']).shortened,
            }
        )
