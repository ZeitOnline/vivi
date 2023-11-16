from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.content.interfaces
import zeit.cms.testing


class TestBannerContentDisplayCheckbox(zeit.cms.testing.ZeitCmsBrowserTestCase):
    login_as = 'zmgr:mgrpw'

    def test_banner_content_has_checkbox(self):
        self.browser.open('http://localhost:8080/++skin++vivi/repository/testcontent')
        self.browser.getLink('Checkout').click()
        self.assertIn('fieldname-banner_content', self.browser.contents)


class TestBannerContentDisplay(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        self.content = ExampleContentType()

    def test_banner_content_has_correct_default_value(self):
        self.assertFalse(zeit.cms.content.interfaces.ICommonMetadata(self.content).banner_content)

    def test_banner_contents_correct_stored_value(self):
        zeit.cms.content.interfaces.ICommonMetadata(self.content).banner_content = False
        self.assertFalse(zeit.cms.content.interfaces.ICommonMetadata(self.content).banner_content)
        zeit.cms.content.interfaces.ICommonMetadata(self.content).banner_content = True
        self.assertTrue(zeit.cms.content.interfaces.ICommonMetadata(self.content).banner_content)
