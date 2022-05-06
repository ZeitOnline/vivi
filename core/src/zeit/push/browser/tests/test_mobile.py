import zeit.push.testing


class FindTitleIntegration(zeit.push.testing.SeleniumTestCase):

    def setUp(self):
        super().setUp()
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.open(s.getLocation().replace('edit', 'edit-social'))

    def test_headline_from_template_is_inserted_as_push_title(self):
        s = self.selenium
        s.waitForElementPresent('form.mobile_payload_template')
        s.select('form.mobile_payload_template', 'label=Foo')
        s.waitForValue('form.mobile_title', 'Default title')


class FindTitleTest(zeit.push.testing.BrowserTestCase):

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
