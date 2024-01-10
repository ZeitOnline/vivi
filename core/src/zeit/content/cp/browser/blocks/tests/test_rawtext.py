import zeit.content.cp
import zeit.content.cp.centerpage
import zeit.content.cp.testing
import zeit.content.text.text


class TestRawText(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('rawtext')
        self.repository['centerpage'] = self.centerpage

        self.plaintext = zeit.content.text.text.Text()
        self.plaintext.text = '<rawcode_reference />'
        self.repository['plaintext'] = self.plaintext

        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_rawtext_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-rawtext'))
        b.open('body/informatives/@@landing-zone-drop-module?block_type=rawtext')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-rawtext'))

    def test_can_create_rawtext_module_by_dropping_content(self):
        b = self.browser
        b.open('body/lead/@@landing-zone-drop?uniqueId=http://xml.zeit.de/plaintext' '&order=top')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-rawtext'))

    def test_rawtext_can_be_referenced(self):
        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Raw text reference').value = self.plaintext.uniqueId
        b.getControl('Apply').click()
        b.open(self.content_url)
        self.assertEllipsis('...http://xml.zeit.de/plaintext...', b.contents)

    def test_rawtext_should_store_parameters(self):
        embed = zeit.content.text.embed.Embed()
        embed.text = '{{module.params.one}}'
        embed.parameter_definition = '{"one": zope.schema.TextLine()}'
        self.repository['embed'] = embed

        b = self.browser
        b.getLink('Edit block properties', index=0).click()
        b.getControl('Raw text reference').value = 'http://xml.zeit.de/embed'
        b.getControl('Apply').click()
        b.open(self.content_url)
        b.getLink('Edit block properties', index=0).click()
        b.getControl('One').value = 'p1'
        b.getControl('Apply').click()
        b.open(self.content_url)
        b.getLink('Edit block properties', index=0).click()
        self.assertEqual('p1', b.getControl('One').value)
