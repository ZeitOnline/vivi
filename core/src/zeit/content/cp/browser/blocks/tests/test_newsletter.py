import zeit.content.cp
import zeit.content.cp.centerpage
import zeit.content.cp.testing


class TestNewsletter(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('newslettersignup')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_newsletter_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        block_type = 'newslettersignup'
        self.assertEqual(1, b.contents.count('type-{}'.format(block_type)))
        b.open('body/informatives/@@landing-zone-drop-module?block_type={}'.format(block_type))
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-{}'.format(block_type)))

    def test_newsletter_is_editable(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Newsletter Signup').displayValue = ['Z+/Abonnenten']
        zeit.content.cp.centerpage._test_helper_cp_changed = False
        b.getControl('Apply').click()
        self.assertTrue(zeit.content.cp.centerpage._test_helper_cp_changed)
        self.assertEllipsis('...Updated on...', b.contents)

        b.open(self.content_url)
        self.assertEllipsis('...Z+/Abonnenten...', b.contents)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual(['Z+/Abonnenten'], b.getControl('Newsletter Signup').displayValue)
