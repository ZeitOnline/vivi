import os
import tempfile
import urllib.error
import zeit.cms.testing
import zope.app.appsetup.product


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

    def test_should_fail_if_stopfile_exists(self):
        handle, filename = tempfile.mkstemp()
        os.close(handle)
        os.unlink(filename)
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        config['stopfile'] = filename

        b = self.browser
        with self.assertNothingRaised():
            b.open(self.check)

        open(filename, 'w').close()
        with self.assertRaises(urllib.error.HTTPError) as info:
            b.open(self.check)
            self.assertEqual(500, info.exception.status)
            self.assertEqual('fail: stopfile %s present' % filename)
