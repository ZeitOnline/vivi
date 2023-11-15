import zeit.content.cp
import zeit.content.cp.centerpage


class TestMarkup(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage['lead'].create_item('markup')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url
        self.xml_url = (
            'http://localhost/++skin++vivi/workingcopy/zope.user/'
            'centerpage/@@xml_source_edit.html'
        )

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

    def test_markdown_alignment_default_is_set(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Contents').value = '**foo**'
        b.getControl('Apply').click()
        b.open(self.xml_url)
        self.assertEllipsis('...align="left"...', b.contents)

    def test_markdown_alignment_center_is_set(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Contents').value = '**foo**'
        align_center = b.getControl('Alignment').options[1]
        b.getControl('Alignment').value = [align_center]
        b.getControl('Apply').click()
        b.open(self.xml_url)
        self.assertEllipsis('...align="center"...', b.contents)
