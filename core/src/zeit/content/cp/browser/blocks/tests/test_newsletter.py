import zeit.content.cp
import zeit.content.cp.centerpage
import zeit.content.cp.testing


class TestNewsletter(zeit.content.cp.testing.BrowserTestCase):

    def setUp(self):
        super(TestNewsletter, self).setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage['lead'].create_item('newslettersignup')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_newsletter_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        block_type = 'newslettersignup'
        self.assertEqual(1, b.contents.count('type-{}'.format(block_type)))
        b.open('informatives/@@landing-zone-drop-module?block_type={}'.format(
            block_type
        ))
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-{}'.format(block_type)))
