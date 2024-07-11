import zeit.cms.testing


class HealthCheckTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    check = 'http://localhost/++skin++vivi/@@health-check'

    def setUp(self):
        super().setUp()
        self.browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])

    def test_should_normally_have_status_200(self):
        b = self.browser
        b.open(self.check)
        self.assertEqual('200 Ok', b.headers['status'])
        self.assertEqual('OK', b.contents)
