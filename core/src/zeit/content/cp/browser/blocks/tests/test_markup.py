import zeit.cms.testing
import zeit.content.cp
import zeit.content.cp.centerpage


class TestMarkup(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def setUp(self):
        super(TestMarkup, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.centerpage = zeit.content.cp.centerpage.CenterPage()
            self.centerpage['lead'].create_item('markup')
            self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_markup_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-markup'))
        b.open('informatives/@@landing-zone-drop-module?block_type=markup')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-markup'))

    def test_text_is_edited_via_markdown(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Contents').value = '**foo**'
        b.getControl('Apply').click()
        b.open(self.content_url)
        self.assertEllipsis('...<strong>foo</strong>...', b.contents)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual('**foo**', b.getControl('Contents').value.strip())
