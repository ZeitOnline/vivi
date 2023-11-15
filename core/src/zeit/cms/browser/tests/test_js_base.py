import zeit.cms.testing


class EvaluateTest(zeit.cms.testing.SeleniumTestCase):
    layer = zeit.cms.testing.WEBDRIVER_LAYER

    def setUp(self):
        super().setUp()
        self.open('/@@/zeit.cms.browser.tests.fixtures/evaluate/index.html')

    def write_html(self, text):
        text = text.replace('\n', ' ')
        self.execute("document.getElementById('foo').innerHTML = '%s'" % text)

    def evaluate_js_and_css(self):
        self.execute('zeit.cms.evaluate_js_and_css(document.getElementById("foo"))')

    def test_loads_external_scripts(self):
        self.write_html('<script type="text/javascript" src="external.js"></script>')
        self.evaluate_js_and_css()
        self.wait_for_condition('zeit.cms.test_external_loaded')

    def test_evaluates_inline_scripts_once(self):
        self.write_html(
            """
        <script type="text/javascript">
          zeit.cms.test_inline_loaded = (zeit.cms.test_inline_loaded || 0) + 1;
        </script>"""
        )
        self.assertEqual(None, self.eval('zeit.cms.test_inline_loaded'))
        self.evaluate_js_and_css()
        self.assertEqual(1, self.eval('zeit.cms.test_inline_loaded'))
        self.evaluate_js_and_css()
        self.assertEqual(1, self.eval('zeit.cms.test_inline_loaded'))

    def test_imports_style_sheets(self):
        s = self.selenium
        s.assertVisible('css=h3')
        self.write_html('<link rel="stylesheet" type="text/css" href="style.css" />')
        self.evaluate_js_and_css()
        s.waitForNotVisible('css=h3')

    def test_evaluates_inline_style_sheets(self):
        s = self.selenium
        s.assertVisible('css=h3')
        self.write_html(
            """
        <style type="text/css">
          h3 {
            display: none;
          }
        </style>"""
        )
        self.evaluate_js_and_css()
        s.assertNotVisible('css=h3')
