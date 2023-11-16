import zeit.cms.testing
import zeit.cms.tests.test_interfaces


class NormalizeFilenameJSTest(
    zeit.cms.testing.SeleniumTestCase, zeit.cms.tests.test_interfaces.NormalizeFilenameTest
):
    layer = zeit.cms.testing.WEBDRIVER_LAYER

    def setUp(self):
        super().setUp()
        self.open('/@@/zeit.cms.browser.tests.fixtures/js.html')

    def normalize(self, text):
        return self.eval('zeit.cms.normalize_filename("%s")' % text)
