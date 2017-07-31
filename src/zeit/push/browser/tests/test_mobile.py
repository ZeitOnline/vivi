import zeit.push.testing
import zeit.cms.testing


class FindTitleIntegration(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.push.testing.WEBDRIVER_LAYER

    def setUp(self):
        super(FindTitleIntegration, self).setUp()
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.open(s.getLocation().replace('edit', 'edit-social'))

    def test_headline_from_template_is_inserted_as_push_title(self):
        s = self.selenium
        s.waitForElementPresent('form.mobile_payload_template')
        s.select('form.mobile_payload_template', 'label=Foo')
        self.assertEqual('Default title', s.getValue('form.mobile_title'))


class FindTitleTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.push.testing.LAYER

    def test_retrieves_default_from_rendered_template(self):
        self.layer['create_template']("""\
        {
          "default_title": "My title",
          {% if True %}
          "stuff": "{{article.title}}"
          {% endif %}
        }
        """, 'template.json')
        b = self.browser
        b.open('http://localhost/++skin++vivi'
               '/zeit.push.payload_template_title?q=template.json')
        self.assertEqual('My title', b.contents)
