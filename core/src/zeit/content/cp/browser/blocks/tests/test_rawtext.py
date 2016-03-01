import zeit.cms.testing
import zeit.content.cp
import zeit.content.cp.centerpage
import zeit.content.text.text


class TestRawText(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    def setUp(self):
        super(TestRawText, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            self.centerpage = zeit.content.cp.centerpage.CenterPage()
            self.centerpage['lead'].create_item('rawtext')
            self.repository['centerpage'] = self.centerpage

            self.plaintext = zeit.content.text.text.Text()
            self.plaintext.text = '<rawcode_reference />'
            self.repository['plaintext'] = self.plaintext

        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_rawtext_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-rawtext'))
        b.open('informatives/@@landing-zone-drop-module?block_type=rawtext')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-rawtext'))

    def test_rawtext_is_edited(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Contents').value = '<rawcode_text>'
        b.getControl('Apply').click()
        b.open(self.content_url)
        self.assertEllipsis('...&lt;rawcode_text...', b.contents)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual(
            '<rawcode_text>',b.getControl('Contents').value.strip())

    def test_rawtext_is_referenced(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('RawText').value = self.plaintext.uniqueId
        b.getControl('Apply').click()
        b.open(self.content_url)
        self.assertEllipsis('...&lt;rawcode_reference...', b.contents)

    def test_rawtext_reference_should_be_preferred(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Contents').value = '<rawcode_text>'
        b.getControl('RawText').value = self.plaintext.uniqueId
        b.getControl('Apply').click()
        b.open(self.content_url)
        self.assertEllipsis('...&lt;rawcode_reference...', b.contents)
