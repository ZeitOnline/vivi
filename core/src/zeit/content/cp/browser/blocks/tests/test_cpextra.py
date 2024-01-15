import zeit.content.cp.centerpage
import zeit.content.cp.testing


class TestCPExtra(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('cpextra')
        self.repository['centerpage'] = self.centerpage

    def test_cp_extras_can_be_edited(self):
        browser = self.browser
        browser.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        browser.open('contents')
        browser.getLink('Edit block properties', index=0).click()
        self.assertIn('Wetter', browser.getControl('CP Extra Id').displayOptions)
        browser.getControl('CP Extra Id').displayValue = ['Wetter']
        browser.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', browser.contents)
