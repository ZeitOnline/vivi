import zeit.push.testing
import zeit.cms.testing


class FindTitleTest(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.push.testing.WEBDRIVER_LAYER

    def setUp(self):
        super(FindTitleTest, self).setUp()
        self.open('/repository/testcontent/@@checkout')
        s = self.selenium
        s.open(s.getLocation().replace('edit', 'edit-social'))

    def test_headline_from_template_is_inserted_as_push_title(self):
        s = self.selenium
        s.waitForElementPresent('form.mobile_payload_template')
        s.select('form.mobile_payload_template', 'label=Foo')
        self.assertEqual('Default title', s.getValue('form.mobile_title'))
