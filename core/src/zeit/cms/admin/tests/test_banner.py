from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.content.interfaces
import zeit.cms.testing


class TestBannerDisplayCheckbox(zeit.cms.testing.ZeitCmsBrowserTestCase):
    login_as = 'zmgr:mgrpw'

    def test_banner_has_checkbox(self):
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink('Checkout').click()
        self.assertIn('fieldname-banner', self.browser.contents)


class TestBannerDisplay(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        self.content = ExampleContentType()

    def test_banner_has_correct_default_value(self):
        self.assertFalse(zeit.cms.content.interfaces.ICommonMetadata(self.content).banner)

    def test_banner_correct_stored_value(self):
        zeit.cms.content.interfaces.ICommonMetadata(self.content).banner = False
        self.assertFalse(zeit.cms.content.interfaces.ICommonMetadata(self.content).banner)
        zeit.cms.content.interfaces.ICommonMetadata(self.content).banner = True
        self.assertTrue(zeit.cms.content.interfaces.ICommonMetadata(self.content).banner)
